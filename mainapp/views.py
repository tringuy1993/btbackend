

# Create your views here.
from .models import NotionalGreeks, ZDTEDates, PartitionedTable
from .serializers import ZDTEDateSerializer

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .data_access.total_gex import get_notional_greeks_0dte, get_all_partioned_tables, get_theo_gamma
from .data_access.utilities import generate_table_names


class hello(APIView):
    def get(self, request, *args, **kwargs):
        response = {'message': 'Welcome to alpha-seekers backtest'}

        return Response(response)


class zdte_dates(APIView):
    def get(self, request, *args, **kwargs):
        serializer = ZDTEDateSerializer(
            ZDTEDates.objects.all(), many=True).data
        return Response(serializer)


class get_table_partitions(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'data': get_all_partioned_tables()})


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
                                          #   end_date = end_date,
                                          expiration=expiration,
                                          trade_time=trade_time,
                                          greek=greek,
                                          all_greeks=all_greeks,)
        result2 = get_theo_gamma(
            trade_date=trade_date, expiration=expiration, trade_time=trade_time)
        # print(result2)
        return Response({"greek_exposure": result, "greek_theo": result2})
