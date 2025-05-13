from scheduling import solver, model, weekly_cover_demands, all_days, all_shifts, all_employees, employees, new_schedule, max_consecutive_days_allowed # type: ignore
from ortools.sat.python import cp_model
import pytest # type: ignore

@pytest.fixture
def solved_schedule():
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)
    assert status in [cp_model.OPTIMAL, cp_model.FEASIBLE], "Solver failed"

    shifts = new_schedule()
    if shifts is None:
        raise pytest.fail("new_schedule returned None.")

    return solver, shifts

def test_shift_coverage(solved_schedule):
    solver, shifts = solved_schedule
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                assert (e, d, s) in shifts, f"Brakuje klucza {e}, {d}, {s} "


def test_one_shift_per_day_rule(solved_schedule):
    solver, shifts = solved_schedule
    for e in all_employees:
        for d in all_days:
            assigned_shifts = sum(solver.Value(shifts[(e, d, s)]) for s in all_shifts)
            assert assigned_shifts <= 1, (
                "test_one_shift_per_day_rule failed"
            )
            print("test_one_shift_per_day_rule passed")

# Availability tests
def test_work_only_when_available(solved_schedule):
    solver, shifts = solved_schedule

    print("Final schedule:")
    for d in all_days:
        print(f"\nDay {d}:")
        for e, employee in enumerate(employees):
            assigned_shifts = []
            for s in all_shifts:
                if (e, d, s) in shifts and solver.Value(shifts[(e, d, s)]) == 1:
                    assigned_shifts.append(s)

            if assigned_shifts:
                print(f"+ {employee.name} → Shifts: {assigned_shifts}")
            else:
                print(f"- {employee.name} is not working.")

        for e, employee in enumerate(employees):
            for d in all_days:
                available_shifts = employee.availability.get(d, [])
                for s in all_shifts:
                    if solver.Value(shifts[(e, d, s)]) == 1:
                        assert s in available_shifts, f"{employee.name} wrongly assigned to shift {s} on day {d}"

        for e, employee in enumerate(employees):
            for d in all_days:
                if d not in employee.availability:
                    for s in all_shifts:
                        assert solver.Value(shifts[(e, d, s)] == 0), f"{employee.name} assigned to shifts {s} on day {d} but not available."


def test_cover_demand_rule(solved_schedule):
    solver, shifts =solved_schedule
    for d, demands in enumerate(weekly_cover_demands):
        for s, required_workers in enumerate(demands):
            assert sum(solver.Value(shifts[(e, d, s)]) for e in all_employees) == required_workers, (
                f"test_cover_demand_rule failed"
            )
            print("test_cover_demand_rule passed")
            # print(f"Day {d}, Shift {s}: Expected {required_workers}, got {assigned_workers}")


def test_max_working_days_week(solved_schedule):
    solver, shifts =solved_schedule
    for e, employee in enumerate(employees):
        working_days = sum(1 for d in all_days
                           if any(solver.Value(shifts[(e,d,s)]) for s in all_shifts)
                           )
        assert working_days <= 5, f"{e.name} exceeded working days limit, working days - {working_days}."


def test_working_hours_not_exceeded(solved_schedule):
    solver, shifts =solved_schedule

    for e, employee in enumerate(employees):
        total_hours = sum(solver.Value(shifts[(e,d,s)] * (8 if s == 0 else 6.5))
                          for d in all_days
                          for s in all_shifts
        )
    assert total_hours <= employee.max_working_hours, f"{employee.name} exceeded working hours limit {total_hours - employee.max_working_hours}"


def test_consecutive_working_days_limit(solved_schedule):
        solver, shifts =solved_schedule

        for e, employee in enumerate(employees):
            max_days_per_week = employee.max_working_days
            max_consecutive_days = max_consecutive_days_allowed(max_days_per_week)
            works  = [sum(solver.Value(shifts[(e, d, s)]) for s in all_shifts) > 0 for d in all_days]

            consecutive_days = 0
            max_consecutive_found = 0

            print(f"\n Employee {employee.name} - max {max_consecutive_days} consecutive days allowed")
            print(f"works: {works}")

            for d in all_days:
                if works[d] > 0:
                    consecutive_days += 1
                    max_consecutive_found = max(consecutive_days, max_consecutive_found)
                else:
                    consecutive_days = 0

            assert max_consecutive_found <= max_consecutive_days, (
                f"Test failed, employee {employee.name} got: {max_consecutive_found} consecutive days, max expected days: {max_consecutive_days}"
            )
            print(f"Employee {employee.name} got: {max_consecutive_found} consecutive days, allowed days: {max_consecutive_days}")

