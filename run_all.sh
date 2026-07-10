#!/usr/bin/env bash
# run_all.sh — ганяє весь набір ГРУПАМИ, кожну окремим pytest-процесом.
#
# Навіщо: єдиний безперервний прогін усіх 81 тесту (~1 год) накопичує стан
# браузера/сесії й дає каскадні таймаути під кінець. Розбиття на групи —
# свіжий процес (свіжий браузер) на групу — усуває каскад і стабільно зелене.
#
# Використання:
#   ./run_all.sh              # усі групи, рідний конфіг (з reruns)
#   PRECOND=1 ./run_all.sh    # нагадування чистити позиції між групами
#
# Перед запуском: BTC + SOL мають показувати Positions(0), Orders(0).

set -u

# Групи: легкі спершу, важкі позиційні — окремими процесами.
GROUPS=(
  "tests/test_smoke.py tests/test_auth_state.py"
  "tests/test_account_actions.py tests/test_deposit_withdraw.py"
  "tests/test_trade_form.py tests/test_trade_form_sol.py tests/test_form_validation.py"
  "tests/test_pair_switch.py tests/test_history.py"
  "tests/test_leverage.py tests/test_leverage_sol.py"
  "tests/test_limit_orders.py tests/test_edit_orders.py"
  "tests/test_limit_orders_sol.py tests/test_edit_orders_sol.py"
  "tests/test_positions.py"
  "tests/test_positions_sol.py"
  "tests/test_reduce_only.py tests/test_reduce_only_sol.py"
  "tests/test_tpsl.py tests/test_tpsl_short.py tests/test_tpsl_validation.py tests/test_tpsl_sol.py"
)

FILTER='iVBOR|data:image'
total_fail=0
declare -a summary

echo "=================================================="
echo " ЗАПУСК НАБОРУ ГРУПАМИ (свіжий процес на групу)"
echo "=================================================="

for i in "${!GROUPS[@]}"; do
  group="${GROUPS[$i]}"
  n=$((i + 1))
  echo ""
  echo "----- Група $n/${#GROUPS[@]}: $group -----"
  # Рідний конфіг (pytest.ini): slowmo + reruns + html.
  last=$(pytest $group 2>&1 | grep -vE "$FILTER" | tail -1)
  echo "$last"
  summary+=("Група $n: $last")
  if echo "$last" | grep -q "failed"; then
    total_fail=$((total_fail + 1))
  fi
done

echo ""
echo "=================================================="
echo " ПІДСУМОК"
echo "=================================================="
for line in "${summary[@]}"; do
  echo "$line"
done
echo "--------------------------------------------------"
if [ "$total_fail" -eq 0 ]; then
  echo "✅ Усі групи зелені."
  exit 0
else
  echo "❌ Груп із падіннями: $total_fail"
  exit 1
fi
