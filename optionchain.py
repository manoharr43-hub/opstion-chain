@st.cache_data(ttl=3600)
def get_option_tokens(api, index, strikes):
    tokens = []

    for strike in strikes:
        ce_symbol = f"{index} {strike} CE"
        pe_symbol = f"{index} {strike} PE"

        ce = api.search_scrip(exchange="NFO", searchtext=ce_symbol)
        pe = api.search_scrip(exchange="NFO", searchtext=pe_symbol)

        token_ce = ce["values"][0]["token"] if ce and "values" in ce else None
        token_pe = pe["values"][0]["token"] if pe and "values" in pe else None

        tokens.append((strike, token_ce, token_pe))

    return tokens
