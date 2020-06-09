import datetime

NIGHT = 0
DAY = 1
EVENING = 2

START_DAY = datetime.datetime(1, 1, 1, 9, 0, 0, 0)          # calculate by UTC. TODO - to match it to the real time in Israel - 09:00
START_EVENING = datetime.datetime(1, 1, 1, 18, 0, 0, 0)     # calculate by UTC. TODO - to match it to the real time in Israel - 16:00
START_NIGHT = datetime.datetime(1, 1, 1, 0, 0, 0, 0)        # calculate by UTC. TODO - to match it to the real time in Israel - 22:00

day_times = ['night', 'day', 'evening']

'''DOZE_NOT_IN_IDLE = "Device Idle (Doze) state change signal received; device not in idle state"
DOZE_IN_IDLE = "Device Idle (Doze) state change signal received; device in idle state"'''

def get_part_of_day(date_time):
    if START_NIGHT.time() <= date_time.time() < START_DAY.time():       # night time
        return day_times[NIGHT]
    elif START_DAY.time() <= date_time.time() < START_EVENING.time():   # day time
        return day_times[DAY]
    else:                                                               # evening time
        return day_times[EVENING]


def get_next_day_time(date_time):
    if get_part_of_day(date_time) == day_times[DAY]:         # night time
        return day_times[EVENING]
    elif get_part_of_day(date_time) == day_times[EVENING]:   # day time
        return day_times[NIGHT]
    else:                                           # evening time
        return day_times[DAY]


def get_next_part_of_day_start_time(date_time):
    if get_next_day_time(date_time) == day_times[DAY]:
        return START_DAY.time()
    elif get_next_day_time(date_time) == day_times[EVENING]:
        return START_EVENING.time()
    else:
        return START_NIGHT.time()


def get_next_date_for_next_time(date_time, next_time):
    if next_time.hour == 0:     # passing between 2 days
        date_time += datetime.timedelta(days=1)
    new_date_time = datetime.datetime(date_time.year, date_time.month, date_time.day, next_time.hour, next_time.minute, next_time.second, next_time.microsecond)
    return new_date_time


'''if classifier:
    # ------++++++ First Method - Random Forest Classifier ++++++------ #
    model = RandomForestClassifier()
    model = SVC()
    model = KNeighborsClassifier(n_neighbors=4)
    model = GaussianProcessClassifier(1.0*RBF(1.0))
    model = DecisionTreeClassifier(max_depth=5)
    model = MLPClassifier(alpha=1, max_iter=1000)
    model = AdaBoostClassifier()
    model = GaussianNB()
    # model = QuadraticDiscriminantAnalysis()     # need more than 1 sample for class

else:
    # ------++++++ First Method - Linear Regression ++++++------ #
    # linear regression model:
    model = LinearRegression()

    # ------++++++ Second Method - Random Forest Regression ++++++------ #
    # Random Forest model:
    model = RandomForestRegressor(max_depth=None, random_state=0)

    # HuberRegressor, TheilSenRegressor are giving negative numbers

    # ------++++++ Third Method - RANSAC Regression ++++++------ #
    # Random RANSAC model:
    model = RANSACRegressor(random_state=42, min_samples=8)

# ++++++------++++++ Continue Same ++++++------++++++ #
model.fit(X_curr_train, y_curr_train)

score = model.score(X_test, y_test)
y_pred = model.predict_proba(X_curr_test)


y_pred = model.predict(X_curr_test)
print('y_test:\n', y_curr_test, '\ny_pred:\n', y_pred)

model.score(X_test, y_test)'''

a = RandomForestClassifier()
a,fit()