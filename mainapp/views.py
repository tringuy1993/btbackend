

# Create your views here.
from .models import ZDTEDates
from .serializers import ZDTEDateSerializer

from rest_framework.response import Response
from rest_framework.views import APIView
from .data_access.total_gex import get_notional_greeks_0dte, get_all_partioned_tables, get_theo_gamma, get_option_chain
from .data_access.queryOrder import queryOrder
from rest_framework.decorators import permission_classes
from .authentication import IsAuthenticatedWithFirebase
import json
from .data_access.opt_chain_multi import get_option_chain_df
from .utility.calc_functions import theo_gamma_data



class hello(APIView):
    def get(self, request, *args, **kwargs):
        response = {'message': 'Welcome to alpha-seekers backtest'}

        return Response(response)


@permission_classes([IsAuthenticatedWithFirebase])
class zdte_dates(APIView):
    def get(self, request, *args, **kwargs):
        serializer = ZDTEDateSerializer(
            ZDTEDates.objects.all(), many=True).data
        return Response(serializer)


@permission_classes([IsAuthenticatedWithFirebase])
class get_table_partitions(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'data': get_all_partioned_tables()})


@permission_classes([IsAuthenticatedWithFirebase])
class my_view(APIView):
    def get(self, request, *args, **kwargs):
        trade_date = request.query_params.get("trade_date").replace('-', '')
        expiration = request.query_params.get("expiration").replace('-', '')
        trade_time = request.query_params.get("trade_time")
        greek = request.query_params.get("greek")
        all_greeks = request.query_params.get("all_greeks")
        table_list = 'spxw_data_p' + trade_date

        result = get_notional_greeks_0dte(tables=table_list,
                                          trade_date=trade_date,
                                          expiration=expiration,
                                          trade_time=trade_time,
                                          greek=greek,
                                          all_greeks=all_greeks,)
        result2 = get_theo_gamma(
            trade_date=trade_date, expiration=expiration, trade_time=trade_time)

        return Response({"greek_exposure": result, "greek_theo": result2})


@permission_classes([IsAuthenticatedWithFirebase])
class option_chain(APIView):
    def get(self, request, *args, **kwargs):
        trade_date = request.query_params.get("trade_date").replace('-', '')
        expiration = request.query_params.get("expiration").replace('-', '')
        trade_time = request.query_params.get("trade_time")
        table = 'spxw_data_p' + trade_date
        result = get_option_chain(
            table=table, expiration=expiration, trade_time=trade_time)

        return Response({'data': result})

@permission_classes([IsAuthenticatedWithFirebase])
class track_order(APIView):
    def get(self, request, *args, **kwargs):
        trade_date = request.query_params.get("trade_date").replace('-', '')
        expiration = request.query_params.get("expiration").replace('-', '')
        trade_time = request.query_params.get("trade_time")
        quote_datetime = trade_date + " " + trade_time
        # print(quote_datetime)
        option_legs = json.loads(request.query_params.get("option_legs"))
        table = 'spxw_data_p' + trade_date
        # print(f'trade_date {trade_date}, trade_time {trade_time}, expiration {expiration}')
        # print('optionlegs:', option_legs)
        results = queryOrder(table=table, expiration=expiration,
                             quote_datetime=quote_datetime, option_legs=option_legs)
        
        return Response({'data': results})

class theo_gamma(APIView):
    def get(self, request, *args, **kwargs):
        # date = '20180601'
        # quote_datetime = date + " " +'11:31:00'
        # expiration = '20180601'
        trade_date = request.query_params.get("trade_date").replace('-', '')
        expiration = request.query_params.get("expiration").replace('-', '')
        trade_time = request.query_params.get("trade_time")
        quote_datetime = trade_date + " " + trade_time
        table = 'spxw_data_p' + trade_date

        data = get_option_chain_df(table, quote_datetime, expiration)
        theo_data = theo_gamma_data(data)



    
        

        return Response({"TheoGamma view": theo_data})