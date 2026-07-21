#!/usr/bin/env bash
# run_all.sh - runs the whole suite in SUITE_GROUPS, each a fresh pytest process.
# Before running: BTC + SOL must show Positions(0), Orders(0), Cross mode.
set -u

SUITE_GROUPS=(
  "tests/test_smoke.py tests/test_auth_state.py"
  "tests/test_account_actions.py tests/test_deposit_withdraw.py"
  "tests/test_trade_form.py tests/test_trade_form_sol.py tests/test_form_validation.py"
  "tests/test_pair_switch.py tests/test_history.py tests/test_history_sol.py"
  "tests/test_leverage.py tests/test_leverage_sol.py"
  "tests/test_order_type_switch.py tests/test_size_percent.py tests/test_tpsl_percent.py"
  "tests/test_sl_validation.py tests/test_tpsl_validation.py"
  "tests/test_margin_mode.py tests/test_margin_mode_sol.py"
  "tests/test_limit_orders.py tests/test_edit_orders.py"
  "tests/test_limit_orders_sol.py tests/test_edit_orders_sol.py"
  "tests/test_positions.py"
  "tests/test_positions_sol.py"
  "tests/test_reduce_only.py tests/test_reduce_only_sol.py"
  "tests/test_tpsl.py tests/test_tpsl_short.py tests/test_tpsl_sol.py tests/test_tpsl_short_sol.py"
  "tests/test_isolated_trading.py tests/test_isolated_trading_sol.py"
  "tests/test_isolated_reduce_only.py tests/test_isolated_reduce_only_sol.py"
  "tests/test_isolated_tpsl.py tests/test_isolated_tpsl_sol.py"
  "tests/test_isolated_leverage.py tests/test_isolated_partial_close.py"
)
FILTER='iVBOR|data:image'
total_fail=0
declare -a summary

echo "=== RUNNING SUITE IN SUITE_GROUPS (fresh process per group) ==="
for i in "${!SUITE_GROUPS[@]}"; do
  group="${SUITE_GROUPS[$i]}"
  n=$((i + 1))
  echo ""
  echo "----- Group $n/${#SUITE_GROUPS[@]}: $group -----"
  last=$(pytest $group 2>&1 | grep -vE "$FILTER" | tail -1)
  echo "$last"
  summary+=("Group $n: $last")
  if echo "$last" | grep -q "failed"; then
    total_fail=$((total_fail + 1))
  fi
done

echo ""
echo "=== SUMMARY ==="
for line in "${summary[@]}"; do
  echo "$line"
done
if [ "$total_fail" -eq 0 ]; then
  echo "OK: all groups green."
  exit 0
else
  echo "FAIL groups: $total_fail"
  exit 1
fi
