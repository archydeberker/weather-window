import models
import datetime

from app_factory import create_app


def main(dry_run=True):
    one_day_ago = datetime.datetime.now() + datetime.timedelta(hours=-24)
    old_forecasts = models.Forecast.query.filter(models.Forecast.recorded_timestamp < one_day_ago)

    if len(old_forecasts.all()) > 0:
        print(f"Delete {len(old_forecasts.all())} records, oldest being {old_forecasts.order_by(models.Forecast.weather_timestamp).first().weather_timestamp} and "
          f"youngest being {old_forecasts.order_by(models.Forecast.weather_timestamp.desc()).first().weather_timestamp}")
    else:
        print(f"Wouldn't delete anything")

    if not dry_run:
        try:
            n_rows = old_forecasts.delete()
            print(f"{n_rows} successfully deleted")
            models.db.session.commit()
        except Exception as e:
            models.db.session.rollback()
            raise e
    else:
        print('Dry run, aborting')


if __name__ == '__main__':
    app = create_app()
    app.app_context().push()

    main(dry_run=False)
