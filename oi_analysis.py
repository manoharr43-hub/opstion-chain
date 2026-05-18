def calculate_pcr(calls, puts):

    total_put_oi = puts['openInterest'].sum()

    total_call_oi = calls['openInterest'].sum()

    if total_call_oi == 0:
        return 0

    return total_put_oi / total_call_oi


def max_pain(calls, puts):

    calls_oi = calls.groupby(
        'strike'
    )['openInterest'].sum()

    puts_oi = puts.groupby(
        'strike'
    )['openInterest'].sum()

    combined = calls_oi + puts_oi

    return combined.idxmax()
