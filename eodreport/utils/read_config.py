# import configparser

# config = configparser.ConfigParser()
# config.optionxform = str
# config.read('config.ini')


def get_quandl_api_key():
    return 'bo-vhkNq8cvCA_cbS8o-'
    # return config['Quandl']['api_key']


def get_iex_p_api_key():
    return 'Tpk_7f7c4a21007e4715a7ff0ab7df7d3330'
    # return config['IEX']['p_api_key']


def get_iex_s_api_key():
    return 'Tsk_904180502b044f2683ea7459a99a5a7a'
    # return config['IEX']['s_api_key']