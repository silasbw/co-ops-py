"""
A wrapper for http://tidesandcurrents.noaa.gov/api/
"""

import datetime
import json
import requests


CO_OPS_DATE_FORMAT = '%Y%m%d %H:%M'  # yyyyMMdd HH:mm


class CoOpsException(RuntimeError):
  pass


def gmtime():
  return datetime.datetime.utcnow().strftime(CO_OPS_DATE_FORMAT)


def get(**params):
  water_level_products = {
      'water_level',
      'hourly_height',
      'high_low',
      'daily_mean',
      'monthly_mean',
      'one_minute_water_level',
      'predictions'}

  params = dict(params)

  if 'format' not in params:
    params['format'] = 'json'
  if 'time_zone' not in params:
    params['time_zone'] = 'gmt'
  if 'units' not in params:
    params['units'] = 'metric'
  if 'application' not in params:
    params['application'] = 'co-ops-py'
  if (('begin_date' not in params) and
      ('end_date' not in params) and
      ('date' not in params) and
      ('range' not in params)):
    params['date'] = 'latest'

  if params.get('product') in water_level_products and ('datum' not in params):
    params['datum'] = 'MLLW'

  result = requests.get('http://tidesandcurrents.noaa.gov/api/datagetter',
                        params=params)
  if result.status_code != 200:
    raise CoOpsException(
        'GET failed ({}): {}'.format(result.status_code, result.text))
  return json.loads(result.text)


if __name__ == '__main__':
  southampton_current = get(
      product='currents', units='english', station='s08010', date='latest')
  current = southampton_current['data'][0]
  print 'current {} kts at {} degrees'.format(current['s'], current['d'])

  richmod_levels = get(product='water_level',
                       units='english',
                       station=9414863,
                       date='latest')
  level = richmod_levels['data'][0]['v']
  print 'current level {} ft'.format(level)

  richmond_predictions = get(
      product='predictions',
      units='english',
      station=9414863,
      begin_date=gmtime(),
      range=1)
  tides = richmond_predictions['predictions']
  print 'prediction {} ft to {} ft'.format(tides[0]['v'], tides[-1]['v'])
