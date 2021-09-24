import requests

from dmiclient.models import Forecast


class DMIClient(object):

    def get_forecast(self, area_id: int) -> Forecast:
        return Forecast.from_remote(
            requests.get('https://www.dmi.dk/NinJo2DmiDk/ninjo2dmidk?cmd=llj&id={}'.format(area_id)).json()['timeserie']
        )
