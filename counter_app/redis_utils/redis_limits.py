import redis
import logging
from datetime import datetime


class RedisAmountLimiter:
    """manages all limits for "AMOUNT_LIMIT_*" throughput"""

    def __init__(self, host, limit_name="", limits=None):
        self.r = redis.Redis(host=host)
        self.initial_limits = None

        if limit_name:
            self.limit_name = limit_name
        if limits:
            self.set_initial_limits(limits)

    def proceed_income_amount(self, income_amount: int):
        try:
            with self.r.pipeline() as pipe:
                # watching on time_keys for data consistency
                for key in self.get_limits_keys():
                    pipe.watch(key)

                # iterate throughout all current values and check if we overcome limit with new data
                updated_limits = {}
                for _limit_key in self.get_limits_keys():
                    proposed_value = self.check_limit_exceed(_limit_key, income_amount)
                    updated_limits[_limit_key] = proposed_value

                pipe.multi()
                self.update_limits(updated_limits)
                pipe.execute()
                result_message = {
                    "result": "OK"
                }
                return result_message

        except redis.WatchError:
            logging.warning("WatchError on limit_key:", key)
        except ValueError as e:
            pipe.unwatch()
            logging.error(e)
            result_message = {
                "error": str(e)
            }
            return result_message

    def set_initial_limits(self, limits: dict):
        logging.info("REDIS INIT: {}:{}".format(self.limit_name, limits))
        self.r.hmset(self.limit_name, limits)
        self.initial_limits = limits

    def update_limits(self, limits: dict):
        self.r.hmset(self.limit_name, limits)

    def get_limit_value(self, limit_key: str):
        return self.r.hget(self.limit_name, limit_key).decode('utf-8')

    def set_limit_value(self, limit_key: str, value: int):
        self.r.hset(self.limit_name, limit_key, value)

    def get_all_limits(self) -> dict:
        limits_mappings = {}
        for k, v in self.r.hgetall(self.limit_name).items():
            key = k.decode('utf-8')
            val = int(v.decode('utf-8'))
            limits_mappings[key] = val
        return limits_mappings

    def get_limits_keys(self) -> list:
        keys = []
        for k in self.r.hgetall(self.limit_name).keys():
            key = k.decode('utf-8')
            keys.append(key)
        return keys

    def check_limit_exceed(self, limit_key: str, value: int):
        current = int(self.get_limit_value(limit_key))
        result = current - value
        if result < 0:
            threshold_time = limit_key
            threshold_amount = self.initial_limits.get(limit_key)
            err_msg = "amount limit exceeded ({}/{}sec)".format(threshold_amount, threshold_time)
            raise ValueError(err_msg)
        return result

    def flush_all_data(self):
        self.r.flushall()

    def reset_limit(self, limit_key):
        print("resetting limits for key:", limit_key)
        print('Tick! The time is: %s' % datetime.now())
        self.set_limit_value(limit_key, self.initial_limits[limit_key])
