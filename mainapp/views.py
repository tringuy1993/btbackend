

# Create your views here.
from .models import NotionalGreeks, ZDTEDates
from .serializers import ZDTEDateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .data_access.total_gex import get_notional_greeks_0dte
from .data_access.utilities import generate_table_names


class hello(APIView):
    def get (self, request, *args, **kwargs):
        response = {'message': 'Welcome to alpha-seekers backtest'}

        return Response(response)

class zdte_dates(APIView):
    def get(self, request, *args, **kwargs):
        serializer = ZDTEDateSerializer(ZDTEDates.objects.all(), many=True).data
        return Response(serializer)
        

class my_view(APIView):
    def get(self, request, *args, **kwargs):
        trade_date = request.query_params.get("trade_date").replace('-','')
        # end_date = request.query_params.get("end_date")
        expiration = request.query_params.get("expiration").replace('-','')
        trade_time = request.query_params.get("trade_time")
        greek = request.query_params.get("greek")
        all_greeks = request.query_params.get("all_greeks")
        table_list = 'dev_spxw_data_p'+ trade_date


        result = get_notional_greeks_0dte(tables=table_list, 
                                          trade_date=trade_date, 
                                        #   end_date = end_date,
                                          expiration=expiration,
                                          trade_time=trade_time,
                                          greek=greek,
                                          all_greeks=all_greeks,)
        
        return Response(result)
    

        # print(trade_date, trade_time, greek)
        # trade_date = '2021-08-04'
        # trade_time = '09:31:00'
        # greek="gamma"
        # table = "dev_spxw_data_p"+start_date.replace('-','')
