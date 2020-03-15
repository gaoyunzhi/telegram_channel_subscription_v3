import time
import yaml

HOUR = 60 * 60

class HOLD(object):
    def __init__(self):
        self.holds = {}

    def hold(self, x, msg=None, hold_hour = 1):
        self.holds[x] = self.holds.get(x, [])
        self.holds[x].append((time.time() + hold_hour * HOUR, msg))

    def onHold(self, x):
        return not not self.holds.get(x)

    def clearHold(self, debug_group):
        for x in self.holds:
            while self.holds[x]:
                t, msg = self.holds[x].pop()
                if t > time.time():
                    continue
                try:
                    r = msg.forward_message(debug_group.id)
                    r.delete()
                except:
                    continue
                break

class CACHE(object):
    def __init__(self):
        self.cache = set()

    def add(self, x):
        if x in self.cache:
            return False
        self.cache.add(x)
        return True

class QUEUE(object):
    def __init__(self):
        try:
            with open('queue.yaml') as f:
                self.queue = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            self.queue = []

    def append(self, x):
        self.queue.append(x)
        self.save()

    def replace(self, x):
        self.queue = x
        self.save()

    def pop(self):
        x = self.queue.pop()
        self.save()
        return x

    def pop_all(self, a, b, d):
        r = [x[2] for x in self.queue if x[0] == a and x[1] == b and x[3] == d]
        self.queue = [x for x in self.queue if not (x[0] == a and x[1] == b and x[3] == d)]
        self.save()
        return r

    def empty(self):
        return len(self.queue) == 0

    def save(self):
        with open('queue.yaml', 'w') as f:
            f.write(yaml.dump(self.queue, sort_keys=True, indent=2))

class SUBSCRIPTION(object):
    def __init__(self):
        try:
            with open('subscription.yaml') as f:
                self.SUBSCRIPTION = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            self.SUBSCRIPTION = {}

    def getList(self, chat_id):
        return self.SUBSCRIPTION.get(chat_id, [])

    def getAll(self):
        r = set()
        for x in self.SUBSCRIPTION:
            r.add(x)
            for y in self.SUBSCRIPTION[x]:
                r.add(y['id'])
        return r

    def deleteIndex(self, chat_id, index):
        try:
            del self.SUBSCRIPTION[chat_id][index]
            self.save()
            return 'success'
        except Exception as e:
            return str(e)

    def getSubsribers(self, chat_id):
        result = []
        for subscriber, items in self.SUBSCRIPTION.items():
            for item in items:
                if item['id'] == chat_id:
                    result.append(subscriber)
                    break
        return result

    def add(self, chat_id, chat):
        self.SUBSCRIPTION[chat_id] = self.SUBSCRIPTION.get(chat_id, [])
        if chat['id'] in [x['id'] for x in self.SUBSCRIPTION[chat_id]]:
            return 'FAIL: subscripion already exist.'
        self.SUBSCRIPTION[chat_id].append(chat)
        self.save()
        return 'success'

    def save(self):
        with open('subscription.yaml', 'w') as f:
            f.write(yaml.dump(self.SUBSCRIPTION, sort_keys=True, indent=2))