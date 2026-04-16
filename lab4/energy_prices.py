import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from sklearn.linear_model import LinearRegression
from prettytable import PrettyTable

# Параметри системи
a, b = 150, 2.5  # a - базовий попит, b - чутливість до ціни
c, d = 30, 3.5  # c - базові витрати, d - чутливість виробництва
gamma = 0.15  # Коефіцієнт швидкості адаптації ціни
p_initial = 10  # Початкова ціна


# Динамічна модель (ЗДР) -> Обчислення похідної ціни по часу dp/dt
def price_derivative(t, p_val):
    q_d = a - b * p_val[0]
    q_s = -c + d * p_val[0]
    return [gamma * (q_d - q_s)]


# Часовий проміжок для моделювання
t_span = (0, 24)
t_eval = np.linspace(t_span[0], t_span[1], 100)

# Розв'язання рівняння
solution = solve_ivp(price_derivative, t_span, [p_initial], t_eval=t_eval)
t_dynamic = np.asarray(solution.t)
P_dynamic = np.asarray(solution.y[0])

# Трендова екстраполяція
train_size = len(t_dynamic) // 3
t_train = t_dynamic[:train_size].reshape(-1, 1)
P_train = P_dynamic[:train_size]

# Навчання моделі
trend_model = LinearRegression()
trend_model.fit(t_train, P_train)

# Екстраполяція на весь проміжок часу
P_trend = trend_model.predict(t_dynamic.reshape(-1, 1))

plt.figure(figsize=(10, 6))

plt.plot(t_dynamic, P_dynamic, label="Динамічна модель (ЗДР)", linewidth=2.5, color="#2ca02c")
plt.plot(t_dynamic, P_trend, '--', label="Трендова екстраполяція", linewidth=2, color="#ff7f0e")

plt.axvline(x=t_dynamic[train_size], color='gray', linestyle=':', label="Межа даних для тренду")

P_equilibrium = (a + c) / (b + d)
plt.axhline(y=P_equilibrium, color='blue', linestyle='-.', alpha=0.5,
            label=f"Рівноважна ціна (P={P_equilibrium:.2f})")

plt.title("Моделювання попиту та пропозиції електроенергії", fontsize=14)
plt.xlabel("Час (t)", fontsize=12)
plt.ylabel("Ціна електроенергії (P)", fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

print("Результати моделювання")
print(f"Ідеальна рівноважна ціна: {P_equilibrium:.2f}")
print(f"Початкова ціна: {p_initial}")

print("\nЯк змінювалась ціна (перші 5 і останні 5 місяців)\n")

table = PrettyTable()
table.field_names = ["Час (t)", "Ціна по моделі (ЗДР)", "Прогноз тренду"]

for i in range(5):
    table.add_row([f"{t_dynamic[i]:.2f}", f"{P_dynamic[i]:.2f}", f"{P_trend[i]:.2f}"])

table.add_row(["...", "...", "..."])

for i in range(len(t_dynamic) - 5, len(t_dynamic)):
    table.add_row([f"{t_dynamic[i]:.2f}", f"{P_dynamic[i]:.2f}", f"{P_trend[i]:.2f}"])

print(table)
plt.show()
