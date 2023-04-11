from datetime import datetime, timedelta



def generate_table_names(start: str, end: str):
    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    # Generate list of dates between start and end dates
    date_range = []
    while start_date <= end_date:
        date_range.append(start_date)
        start_date += timedelta(days=1)

    # Convert dates to desired format and add to list of table names
    table_names = []
    for date in date_range:
        table_name = 'dev_spxw_data_p' + date.strftime('%Y%m%d')
        table_names.append(table_name)

    return table_names