from ortools.sat.python import cp_model
from datetime import datetime
from collections import defaultdict

class Employees:
    def __init__(self, name, preferred_shifts, availability, shift_requests, max_working_hours):
        self.name = name
        self.preferred_shifts = preferred_shifts
        self.availability = availability
        self.shift_requests = shift_requests
        self.max_working_hours = max_working_hours
        self.max_working_days = self.max_working_hours//8

employees = [
    Employees(
        "Ola",
        [0, 1], # 0 - morning shift, 1 - afternoon shift
        {
            0: [0,1],
            # 0: [0, 1],
            1: [0, 1],
            2: [0, 1],
            3: [0, 1],
            4: [0],
            5: [0],
            6: [0, 1]
        },
        [],
        40
    ),
    Employees(
        "Marek",
        [0, 1],
        {
            0: [0, 1],
            1: [0],
            2: [0],
            3: [0],
            4: [],
            5: [0, 1],
            6: [],
        },
        [],
        30
    ),
    Employees(
        "Kasia",
        [1],
        {
            0: [1],
            1: [],
            2: [0, 1],
            3: [1],
            4: [],
            5: [0, 1],
            6: [0, 1],
        },
        [],
        20
    ),
    Employees(
        "Kasia 2",
        [1],
        {
            0: [1],
            1: [],
            2: [0, 1],
            3: [1],
            4: [],
            5: [0, 1],
            6: [0, 1],
        },
        [],
        20
    ),
    Employees(
        "Jan",
        [1],
        {
            0: [],
            1: [1],
            2: [1],
            3: [1],
            4: [1],
            5: [1],
            6: []
        },
        [],
        16
    ),
    Employees(
        "Zosia",
        [1],
        {
            0: [],
            1: [],
            2: [1],
            3: [1],
            4: [1],
            5: [],
            6: [],
        },
        [],
        16
    ),
    Employees(
        "Grzegorz",
        [0, 1],
        {
            0: [0, 1],
            1: [0, 1],
            2: [0, 1],
            3: [0, 1],
            4: [0],
            5: [0],
            6: [0, 1]
        },
        [],
        32
    ),
    Employees(
        "Ania",
        [0, 1],
        {
            0: [],
            1: [],
            2: [0, 1],
            3: [0, 1],
            4: [0, 1],
            5: [0, 1],
            6: [0, 1]
        },
        [],
        16
    ),
    Employees(
        "Krzysiek",
        [0, 1],
        {
            0: [0, 1],
            1: [0, 1],
            2: [0, 1],
            3: [0, 1],
            4: [0],
            5: [0],
            6: [0, 1]
        },
        [],
        32
    ),
]

shifts_type = [0, 1]
num_employees = len(employees)
all_employees = range(num_employees)
all_shifts = range(2)
all_days = range(7)
shifts_per_day = 1
weekly_cover_demands = [
(1, 2),
(2, 2),
(2, 2),
(2, 2),
(1, 2),
(2, 2),
(2, 3),
]
time_between_shifts = None
max_working_hours_per_week = 40
num_shifts = sum(morning + afternoon for morning, afternoon in weekly_cover_demands)

start_m_shift = '07:00:00'
end_m_shift = '15:00:00'
start_a_shift = '14:30:00'
end_a_shift = '21:00:00'
FMT = '%H:%M:%S'
morning_shift_duration = (datetime.strptime(end_m_shift, FMT) - datetime.strptime(start_m_shift, FMT)).total_seconds()/3600
afternoon_shift_duration = (datetime.strptime(end_a_shift, FMT) - datetime.strptime(start_a_shift, FMT)).total_seconds()/3600
shift_durations = {
    0: (datetime.strptime(end_m_shift, FMT) - datetime.strptime(start_m_shift, FMT)).total_seconds()/3600,
    1: (datetime.strptime(end_a_shift, FMT) - datetime.strptime(start_a_shift, FMT)).total_seconds()/3600
}

def basic_diagnosis():
# Wyliczanie dostępnych godzin pracowników i zapotrzebowania
    total_hours_needed = sum(morning_shift_duration * morning + afternoon_shift_duration * afternoon for morning, afternoon in weekly_cover_demands)
    total_hours_available = sum(emp.max_working_hours for emp in employees)
    deficit = total_hours_needed - total_hours_available

    if total_hours_available < total_hours_needed:
        print(f"\n ! Brak godzin: potrzebne {total_hours_needed}, dostępne {total_hours_available}, brakuje: {deficit}")
    else:
        print(f"\nWorking hours after considering shift cover demands: {total_hours_needed}")
        print(f"Employees available hours: {total_hours_available}")

# Wyliczanie limitów pracowników
    print("\nLimity pracowników")
    for emp in employees:
        available_days= sum(1 for d in all_days if any(s in emp.availability.get(d, []) for s in all_shifts))
        print(f"{emp.name}: max hours - {emp.max_working_hours}, available days - {available_days}")

def max_consecutive_days_allowed(MDaysPerWeek):
    if MDaysPerWeek == 5:
        return 4
    elif MDaysPerWeek == 4:
        return 3
    elif MDaysPerWeek == 3:
        return 2
    else:
        return MDaysPerWeek

class OptimalSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, shifts, employees, all_days,
                 all_shifts, violations, total_worked_minutes, solution_limit=3):
        super().__init__()
        self.shifts = shifts
        self.employees = employees
        self.all_days = all_days
        self.all_shifts = all_shifts
        self.violations = violations
        self.total_worked_minutes = total_worked_minutes
        self.solution_count = 0
        self.solutions = []
        self.solution_limit = solution_limit

    def on_solution_callback(self):
        self.solution_count += 1

        shortage_score = sum(self.Value(self.violations[f"coverage_d{d}_s{s}"]) for d in self.all_days for s in self.all_shifts)
        shortage_week = defaultdict(list)
        for d in self.all_days:
            for s in self.all_shifts:
                shortage_week[d].append(self.Value(self.violations[f"coverage_d{d}_s{s}"]))

        total_score = (
            shortage_score * 1000
        )
        total_work = {}
        for e, emp in enumerate(self.employees):
            minutes = self.Value(total_worked_minutes[e])
            hours = minutes/60
            total_work[e] = hours

        solution = {
            'shortage': shortage_score,
            'shortage_week': shortage_week,
            'total_worked_time': total_work,
            'total_score': total_score,
            'solution_id': self.solution_count,
            'values': {(e, d, s): self.Value(self.shifts[(e, d, s)])
                       for e in all_employees
                       for d in self.all_days
                       for s in self.all_shifts
                       }
        }

        self.solutions.append(solution)

    def print_sorted_solutions(self):
        self.solutions.sort(key=lambda x: x['total_score'])

        for i, sol in enumerate(self.solutions[:self.solution_limit], 1):
            print(f"\nRozwiązanie {i}, total score: {sol['total_score']}")
            self.print_single_solution(sol,)

    def print_single_solution(self, solution):

        for d in all_days:
            print(f"Dzień {d+1}")
            assigned_employees = set()
            for e, employee in enumerate(employees):
                for s in all_shifts:
                    if solution['values'].get((e, d, s), 0):
                        print(f"{employee.name} pracuje", f"{'na zmianie 0' if s == 0 else 'na zmianie 1'}" )
                        assigned_employees.add(e)

            for s in all_shifts:
                if solution['shortage_week'][d][s] > 0:
                    print(f"[KRYTYCZNY] Braki pracowników na dzień {d+1} na zmianę {s}")
                    available_employees = [employee.name for e, employee in enumerate(employees)
                           if s in employee.availability.get(d, [])
                           and e not in assigned_employees
                           and employee.max_working_hours - solution['total_worked_time'][e] >= shift_durations[s]]
                    could_work = [employee.name for e, employee in enumerate(employees)
                                  if e not in assigned_employees
                                  and solution['total_worked_time'][e] + shift_durations[s] <= max_working_hours_per_week]
                    print("Dostępni, nieprzypisani:",available_employees,)
                    print("Poproś o przyjęcie zmiany: ", could_work, "\n")

        print(f"\nGodziny pracy:")
        for e, emp in enumerate(employees):
            coverage_percent = round((solution['total_worked_time'][e]/emp.max_working_hours) * 100, 2)
            print(f"{emp.name} pracuje {solution['total_worked_time'][e]}h/{emp.max_working_hours}h | {coverage_percent}% dyspozycji", "| " f"{'[za mało godzin]' if coverage_percent < 80 else ''}")

    def get_best_solution(self):
        if self.solutions:
            print("\nNajlepsze rozwiązanie:")
            print(self.solutions[0])
        return "Brak najlepszego rozwiązania"

    def get_solution_count(self):
        return self.solution_count

def build_base_model():
    model = cp_model.CpModel()

    shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.NewBoolVar(f"shift_e{e}_d{d}_s{s}")
    return model, shifts

def add_hard_constraints(model, shifts):
# One shift per day constraint
    for e in all_employees:
        for d in all_days:
            model.AddAtMostOne([shifts[(e, d, s)] for s in all_shifts])

# Availability constraint
    for e, employee in enumerate(employees):
        # print(f"{employee.name} availability: {employee.availability}")
        for d in all_days:
            shifts_available = employee.availability.get(d, [])
            for s in all_shifts:
                if s not in shifts_available:
                    # print(f"Checking: {employee.name}, day {d}, shift {s} - Allowed shifts: {employee.availability.get(d, [])}")
                    model.Add(shifts[(e, d, s)] == 0)
                    # print(f"Restriction added, {employee.name} cant work on day {d}, shift {s}")

# Max working days in a week constraint
    for e, employee in enumerate(employees):
        maxDaysPerWeek = 5
        worked_days = []

        for d in all_days:
            worked_today = model.NewBoolVar(f"worked_e{e}_d{d}")
            model.Add(worked_today == sum(shifts[(e, d, s)] for s in all_shifts))
            worked_days.append(worked_today)

        model.Add(sum(worked_days) <= maxDaysPerWeek)

# Coverage of demands soft constraint
def add_soft_coverage(model, shifts):
    violations = {}
    for d, (morning_demand, afternoon_demand) in enumerate(weekly_cover_demands):
        for s, demand in enumerate([morning_demand, afternoon_demand]):

            shortage = model.NewIntVar(0, demand, f"shortage_d{d}_s{s}")

            model.Add(sum(shifts[(e,d,s)] for e in all_employees) + shortage == demand)
            violations[f"coverage_d{d}_s{s}"] = shortage
    return violations


# Working hours constraint
def add_working_hours_constraint(model, shifts):
    total_worked_minutes = {}
    shift_durations_min = {
        0: 480,  # 8
        1: 390   # 6.5
    }

    for e, employee in enumerate(employees):
        max_working_minutes = employee.max_working_hours * 60
        worked_minutes_var = model.NewIntVar(0, max_working_minutes, f"worked_minutes_{e}")
        model.Add(
            worked_minutes_var == sum(
                shifts[(e, d, s)] * shift_durations_min[s]
                for d in all_days
                for s in all_shifts
            )
        )
        model.Add(worked_minutes_var <= employee.max_working_hours * 60)
        total_worked_minutes[e] = worked_minutes_var

# Maximize equal shift assignment
    coverage_percentage = {}
    min_coverage = model.NewIntVar(0, 100, "min_coverage")
    for e, employee in enumerate(employees):
        coverage_percentage[e] = model.NewIntVar(0, 100, f"coverage percentage_{e}")
        scaled_minutes = model.NewIntVar(0, max_working_minutes * 100, f"scaled_minutes")
        model.Add(scaled_minutes == total_worked_minutes[e]*100)
        model.AddDivisionEquality(coverage_percentage[e], scaled_minutes, max_working_minutes)
        model.Add(min_coverage <= coverage_percentage[e])

    model.Maximize(min_coverage * 1000 + sum(total_worked_minutes[e] for e in all_employees))
    return total_worked_minutes

def add_consecutive_working_days_constraint(model, shifts):
    for e, employee in enumerate(employees):

        max_days_per_week = employee.max_working_days
        max_consecutive_days = max_consecutive_days_allowed(max_days_per_week)

        works = [model.NewBoolVar(f"works_{e}_{d}") for d in all_days]

        for d in range(len(all_days)-max_consecutive_days + 1):
            model.Add(sum(works[d:d+max_consecutive_days+ 1]) <= max_consecutive_days)

def add_shift_preferences(model, shifts):
    preference_score = model.NewIntVar(0, num_shifts, "preference_score")
    preferred_assignments = []

    for e, employee in enumerate(employees):
        for d in all_days:
            for s in all_shifts:
                if s in employee.preferred_shifts:
                    preference_score += 1
                    preferred_assignments.append(shifts[e, d, s])

    model.Add(preference_score == sum(preferred_assignments))
    model.Maximize(preference_score)

if __name__ == "__main__":
    basic_diagnosis()
    model, shifts = build_base_model()
    add_hard_constraints(model, shifts)
    # add_working_hours_constraint(model, shifts)
    total_worked_minutes = add_working_hours_constraint(model, shifts)
    add_consecutive_working_days_constraint(model, shifts)
    violations = add_soft_coverage(model, shifts)
    print("Liczba ograniczeń:", len(model.Proto().constraints))

    solution_printer = OptimalSolutionPrinter(shifts, employees, all_days, all_shifts, violations, total_worked_minutes, 3)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 180
    status = solver.Solve(model, solution_printer)
    solution_printer.print_sorted_solutions()
    solution_printer.get_best_solution()

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("\nPodsumowanie naruszeń:")
        any_violations = False
        for d in all_days:
            for s in all_shifts:
                shortage = solver.Value(violations[f"coverage_d{d}_s{s}"])
                if shortage > 0:
                    any_violations = True
                    print(f"Dzień {d+1}, zmiana {s}: brakuje {shortage} pracowników")

        if not any_violations:
            print("Brak naruszeń, wszystkie zmiany zostały pokryte.")

    else:
        print("Nie znaleziono rozwiązania")
        print(f"- Liczba konfliktów: {solver.num_conflicts}")
        print(f"- Czas: {solver.wall_time}")
        print(f"Znalezione rozwiązania: {solution_printer.get_solution_count()}")