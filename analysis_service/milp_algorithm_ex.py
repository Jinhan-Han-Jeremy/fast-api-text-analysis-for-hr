from ortools.linear_solver import pywraplp
import itertools
import asyncio
from typing import List, Dict, Any

class ParallelTeamScheduler:
    """
    병렬 팀 스케줄링을 처리하기 위한 MILP 최적화 클래스.
    """

    def __init__(self, tasks: List[str], member_performances: List[Dict[str, Any]]):

        self.results = ""  # 최종 결과(문자열 형태)를 저장하기 위함
        self.tasks = tasks  # 작업(Tasks) 목록
        self.member_performances = member_performances  # 작업자(Workers)와 퍼포먼스 목록

        # 먼저 member_performances를 할당한 후 workers를 정의합니다.
        self.workers = list({worker for performance in self.member_performances for worker in performance.keys()})  # 작업자(Workers) 목록
        
        self.tasks_paired_team = []
        self.durations_for_tasks = []
        self.time_requirements = {}  # 각 작업-작업자별 시간 데이터 (None이면 불가)
        self.task_teams = {}  # 작업별로 "가능한 팀(부분집합)" 정보
        self.solver = None  # OR-Tools MIP Solver
        # MILP에서 사용하는 변수들
        self.variables = {
            "x": {},   # x[(task, team)] : team이 task를 맡으면 1, 아니면0
            "s": {},   # s[task] : 작업 task의 시작 시각
            "time_var": None,  # Makespan
            "order_var": {}    # order_var[(task_i, task_j)] : 순서 결정용 이진변수
        }
    
    def define_data(self):
        """
        작업, 작업자, 작업 시간 데이터를 정의한다.
           실제로는 외부에서 읽어올 수도 있음.
        """

        # time_requirements[작업][작업자] = 단독 수행시간
        # None -> 수행 불가능
        # 먼저 time_requirements 생성
        time_requirements: List[Dict[str, Any]] = [
            {worker: performance.get(worker, None) for worker in self.workers}
            for performance in self.member_performances
        ]

        # time_requirements를 self.time_requirements에 매핑
        self.time_requirements: Dict[str, Dict[str, Any]] = {
            task: requirement for task, requirement in zip(self.tasks, time_requirements)
        }
        

    ## 할당인원 제약수
    def get_num_of_assigns(self):
        
        if len(self.workers) < 3:
            num_of_assigns = len(self.workers)%3
        elif len(self.workers) > 3 and len(self.workers) < 10:        
            num_of_assigns= len(self.workers)//3
        elif len(self.workers) > 9:
            num_of_assigns= 3
        
        remainder = len(self.workers)%3
        return num_of_assigns, remainder
    
    def get_longest_task_indices(self):
        ##가장 긴 리스트 인덱스
        max_index = max(range(len(self.member_performances)), key=lambda i: len(self.member_performances[i]))

        ##두 번째로 긴 리스트의 인덱스
        second_max_index = max(
            (i for i in range(len(self.member_performances)) if i != max_index),
            key=lambda i: len(self.member_performances[i])
        )

        return max_index, second_max_index


    def calculate_team_size(self, task, num_of_assigns, remainder, max_index, second_max_index):
        """각 작업별로 적절한 팀 크기를 계산하는 함수"""
        idx = self.tasks.index(task)  # 현재 작업(task)의 인덱스 찾기
        dict_length = len(self.member_performances[idx])  # 해당 작업의 작업자 수

        actual_team_size = num_of_assigns  # 기본 할당 팀 크기

        # 가장 긴 리스트에 대한 팀 크기 조정
        if task == self.tasks[max_index]:
            if remainder < 2:
                actual_team_size += remainder
            elif remainder >= 2 and dict_length > 3:
                actual_team_size += remainder // 2

        # 두 번째로 긴 리스트에 대한 팀 크기 조정
        elif task == self.tasks[second_max_index] and remainder >= 2 and dict_length > 3:
            actual_team_size += remainder // 2

        return actual_team_size


    def filter_feasible_workers(self, task):
        """작업을 수행할 수 있는 작업자 필터링"""
        return [
            w for w in self.workers
            if self.time_requirements[task].get(w) is not None  # 수행 가능한 작업자만 포함
        ]


    def generate_team_combinations(self, task, feasible_workers, actual_team_size):
        """가능한 팀 조합을 생성하고 수행 시간을 계산하는 함수"""
        teams = []

        # 팀 크기 검증 (최소 1명, 최대 feasible_workers 크기 제한)
        actual_team_size = max(1, min(actual_team_size, len(feasible_workers), 3))

        # 가능한 모든 팀 조합 생성 및 수행 시간 계산
        for subset in itertools.combinations(feasible_workers, actual_team_size):
            speed_sum = sum(1.0 / self.time_requirements[task][w] for w in subset)
            duration = 1.0 / speed_sum if speed_sum > 0 else None
            teams.append((subset, duration))

        return teams


    def generate_teams(self):
        """각 작업에 대해 팀을 생성하는 메인 함수"""
        num_of_assigns, remainder = self.get_num_of_assigns()  # 할당할 인원 수 계산
        max_index, second_max_index = self.get_longest_task_indices()  # 가장 긴, 두 번째로 긴 리스트 인덱스 찾기

        self.task_teams = {}

        for task in self.tasks:
            actual_team_size = self.calculate_team_size(task, num_of_assigns, remainder, max_index, second_max_index)  # 팀 크기 결정
            feasible_workers = self.filter_feasible_workers(task)  # 작업 가능한 작업자 필터링
            teams = self.generate_team_combinations(task, feasible_workers, actual_team_size)  # 팀 조합 생성

            self.task_teams[task] = teams  # 결과 저장

    def create_solver(self):
        """
        3) MILP 문제를 해결하기 위한 솔버 생성 시도(SCIP->CBC).
        """
        self.solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.solver:
            self.solver = pywraplp.Solver.CreateSolver('CBC')
        if not self.solver:
            self.results += "No solver available.\n"
            return False
        return True

    def define_variables(self):
        """
        4) MILP에서 사용할 변수 정의.

           - x[(task, team)] : 팀 'team'이 작업 'task'에 배정되면1, 아니면0
           - s[task] : 작업 시작시각(실수값)
           - time_var : Makespan(전체 완료시각)
           - order_var[(t_i, t_j)] : t_i가 t_j보다 먼저면1, 아니면0(선후관계)
        """
        x = {}
        for task in self.tasks:
            for (team, duration) in self.task_teams[task]:
                # 이진변수 0~1
                x[(task, team)] = self.solver.IntVar(0, 1, f"x_{task}_{team}")

        s = {
            task: self.solver.NumVar(0, self.solver.infinity(), f"s_{task}")
            for task in self.tasks
        }
        time_var = self.solver.NumVar(0, self.solver.infinity(), "Makespan")

        order_var = {}
        for i in range(len(self.tasks)):
            for j in range(i + 1, len(self.tasks)):
                order_var[(self.tasks[i], self.tasks[j])] = self.solver.IntVar(
                    0, 1,
                    f"order_{self.tasks[i]}_{self.tasks[j]}"
                )

        self.variables = {"x": x, "s": s, "time_var": time_var, "order_var": order_var}

    def add_constraints(self):
        """
        5) MILP 제약 조건 추가.

        (a) 각 작업은 가능한 2인 팀 중 정확히 1개를 선택
        (b) 한 사람이 여러 작업에 배정되지 않도록 -> sum(...) <= 1
        (c) 겹치는 인력이면 시간 겹침 불가 -> Big-M 선후관계
        (d) time_var >= s[task] + duration
        """
        x = self.variables["x"]
        s = self.variables["s"]
        time_var = self.variables["time_var"]
        order_var = self.variables["order_var"]

        # (a) 각 작업은 "2인 팀" 후보 중 정확히 1개를 선택
        for task in self.tasks:
            self.solver.Add(
                sum(x[(task, team)] for (team, _) in self.task_teams[task]) == 1
            )

        # (b) 한 사람이 여러 작업에 중복 배정되지 않도록 -> 각 worker에 대해
        for worker in self.workers:
            overlapping_tasks = []
            for task in self.tasks:
                for (team, _) in self.task_teams[task]:
                    if worker in team:
                        overlapping_tasks.append(x[(task, team)])
            # 해당 worker가 참여한 팀들의 x값 합 <= 1
            self.solver.Add(sum(overlapping_tasks) <= 1)

        # (c) 겹치는 인력 -> 시간축 겹침 불가 (Big-M)
        bigM = 9999
        for i in range(len(self.tasks)):
            for j in range(i + 1, len(self.tasks)):
                t_i = self.tasks[i]
                t_j = self.tasks[j]
                for (team_i, dur_i) in self.task_teams[t_i]:
                    for (team_j, dur_j) in self.task_teams[t_j]:
                        # 팀 간 공통 인력이 있으면
                        if set(team_i).intersection(set(team_j)):
                            # t_j 시작 >= t_i 종료 - M*(1 - order_var[(t_i,t_j)])
                            self.solver.Add(
                                s[t_j] >= s[t_i] + dur_i
                                         - bigM * (1 - order_var[(t_i, t_j)])
                            )
                            # t_i 시작 >= t_j 종료 - M*(order_var[(t_i,t_j)])
                            self.solver.Add(
                                s[t_i] >= s[t_j] + dur_j
                                         - bigM * order_var[(t_i, t_j)]
                            )

        # (d) Makespan >= s[task] + duration
        for task in self.tasks:
            for (team, duration) in self.task_teams[task]:
                self.solver.Add(time_var >= s[task] + duration)

    def set_objective(self):
        """
        목표함수: Minimize time_var (전체 완료시간)
        """
        time_var = self.variables["time_var"]
        self.solver.Minimize(time_var)

    def solve(self):
        """
        7) Solver 실행 & 결과 기록
        """
        status = self.solver.Solve()
        x = self.variables["x"]
        s = self.variables["s"]
        time_var = self.variables["time_var"]

        if status == pywraplp.Solver.OPTIMAL:
            
            self.results += "[OPTIMAL] 해 발견\n"
            self.results += f"최소 Makespan: {time_var.solution_value():.2f} 시간\n\n"
            
            teams =[]
            durations_for_tasks = []
            for task in self.tasks:
                # 어떤 팀이 선택되었는지 확인 (x=1)
                for (team, duration) in self.task_teams[task]:
                    if x[(task, team)].solution_value() > 0.5:
                        
                        
                        start_time = s[task].solution_value()
                        end_time = start_time + duration
                        
                        ##tasks_paired_team에 알맞은 형태로 데이터 추가가
                        self.tasks_paired_team.append({task: (list(team), float(f"{duration:.2f}"))})
                        
                        #tasks_paired_team에 필요한 요소들 분리 추가
                        teams.append(team)
                        durations_for_tasks.append(float(f"{duration:.2f}"))
                        
                        team_str = ", ".join(team)
                        self.results += f"[작업 {task}]\n"
                        
                        self.results += f"  배정 팀: {team_str} (소요: {duration:.2f})\n"
                        self.results += f"  시작: {start_time:.2f}, 종료: {end_time:.2f}\n\n"
            
            self.results += f"총 완료시각 = {time_var.solution_value():.2f} \n"
            
            print(self.tasks_paired_team)
            
            print(self.tasks)
            
            self.task_teams = list(teams) 
            
            print(self.get_results_teams())
            
            self.durations_for_tasks = durations_for_tasks
            
            print(self.durations_for_tasks)
            
        else:
            
            self.results += f"Solver ended with status={status} (not OPTIMAL)\n"

    def get_results_teams(self):
        if not isinstance(self.task_teams, list):
            self.task_teams = list(self.task_teams)
            
        return self.task_teams

    def get_results(self):
        """최종 결과 문자열 반환."""
        return self.results
    
    def get_results_to_pass(self):
        """MILP 결과 반환"""
        
        return {
        "tasks": self.tasks,
        "teams": self.get_results_teams(),
        "durations": self.durations_for_tasks if self.durations_for_tasks is not None else []
        }
    
async def run_milp_scheduler(tasks, member_performances):
    # tasks, member_performances
    """MILP 알고리즘 실행을 관리하는 비동기 함수"""
    loop = asyncio.get_running_loop()

    scheduler = ParallelTeamScheduler(tasks, member_performances)
    scheduler.define_data()
    scheduler.generate_teams()

    if scheduler.create_solver():
        scheduler.define_variables()
        scheduler.add_constraints()
        scheduler.set_objective()

        # solve()는 동기 함수이므로 별도 스레드에서 실행
        await loop.run_in_executor(None, scheduler.solve)

        # 결과 반환
        return scheduler.get_results_to_pass()
    
    return {"error": "Solver could not be created."}


# if __name__ == "__main__":
#     scheduler = ParallelTeamScheduler()
#     scheduler.define_data()      #  데이터 정의
#     scheduler.generate_teams()   #  " num_of_assigns명수로 팀" 후보 생성
#     if scheduler.create_solver():#  솔버 준비
#         scheduler.define_variables() #  변수 정의
#         scheduler.add_constraints()  #  제약 추가
#         scheduler.set_objective()    #  목표함수 설정
#         scheduler.solve()            #  풀이 및 결과 저장

#     print(scheduler.get_results())