function StorageManager(id, storeFunc){
    this.id = id;
    this.free = typeof(Storage) !== "undefined";

    this.getStorage = storeFunc;

    if(this.free){
        if(this.getStorage().getItem(this.id) == null){
            this.getStorage().setItem(id, "{}");
        }
    }

    this.clear = function(){
        delete this.getStorage()[id];
    };

    this.getEvents = function(func){
        var dayEvents = {};
        if(this.free){
            var dStorage = JSON.parse(this.getStorage().getItem(this.id));
            if(dStorage != null) {
                for (var key in dStorage) {
                    dayEvents[key] = new DayEvent(dStorage[key].year, dStorage[key].month, dStorage[key].day);
                    dayEvents[key].callback = func;
                    for (var key2 in dStorage[key].events) {
                        dayEvents[key].events[key2] = new SingleEvent(dStorage[key].events[key2].name, dStorage[key].events[key2].time);
                    }
                }
            }
        }
        return dayEvents;
    };

    this.syncEvent = function(dEvent){
        if(this.free){
            var dayEvents = JSON.parse(this.getStorage().getItem(this.id));
            if(dayEvents == null){
                dayEvents = {};
            }
            dayEvents[dEvent.key()] = dEvent;
            this.getStorage().setItem(this.id, JSON.stringify(dayEvents));
        }
    }
}


function FunctionObject(func, arg1, arg2){
    this.func = func;
    this.arg1 = arg1;
    this.arg2 = arg2;

    this.execute = function(size){
        this.func(size, this.arg1, this.arg2);
    }
}

var WindowManager = new function(){
    var height = window.innerHeight;
    var width = window.innerWidth;
    var widthFunctions = {};
    var heightFunctions = {};

    this.onHeight = function(name, func, arg1, arg2){
        heightFunctions[name] = new FunctionObject(func, arg1, arg2);
    };

    this.onWidth = function(name, func, arg1, arg2){
        widthFunctions[name] = new FunctionObject(func, arg1, arg2);
    };

    window.onresize = function(event){
        if(width != window.innerWidth){
            width = window.innerWidth;
            for (var key in widthFunctions) {
                if (widthFunctions.hasOwnProperty(key)) {
                    widthFunctions[key].execute(width);
                }
            }
        }
        if(height != window.innerHeight){
            height = window.innerHeight;
            for (var key in heightFunctions) {
                if (heightFunctions.hasOwnProperty(key)) {
                    heightFunctions[key].execute(height);
                }
            }
        }
    };
};

function DateObject(id, year, month, day){
    this.id = id;
    this.year = year;
    this.month = month;
    this.day = day;
}

function MonthInfo(year, month){
    month = parseInt(month);
    year = parseInt(year);
    if (month < 1) {
        month = 12;
        year -= 1;
    }
    if (month > 12) {
        month = 1;
        year += 1;
    }

    var date = new Date(year, month, 0);

    this.numDays = date.getDate();
    this.lastDay = date.getDay();

    date.setDate(1);

    this.firstPosition = date.getDay();
    this.numDaysPrevious = new Date(year, month-1, 0).getDate();
    this.year = year;
    this.month = month;
}

function SingleEvent(name, time){
    this.name = name;
    this.time = time;
    var t = time.split(':');
    this.hour = parseInt(t[0]);
    this.minute = parseInt(t[1]);
    this.meridiem = t[2];

    var md = __zeroFill(this.minute, 2);

    if(this.meridiem != 'all') {
        this.mTime = this.meridiem.toLowerCase() == 'am' ? parseInt(this.hour + md) : parseInt((this.hour + 12) + md);

        var m = " ";
        if (this.minute != 0) {
            m = ":" + md + " ";
        }
        this.timeFormat = this.hour + m + this.meridiem.toLowerCase();
    }else{
        this.mTime = 0;
        this.timeFormat = 'All Day';
    }

    this.key = function(){
        return this.name + ":" + this.time;
    };
}

function DayEvent(year, month, day){
    this.year = year;
    this.month = month;
    this.day = day;

    this.events = {};

    this.sort = function(){
        var a = [];
        for(var key in this.events){
            if(this.events.hasOwnProperty(key)){
                a.push(this.events[key]);
            }
        }
        a = a.sort(__dynamicSort('name')).sort(__dynamicSort('mTime'));
        this.events = {};
        for(var item in a){
            this.events[a[item].key()] = a[item];
        }
    };

    this.addEvent = function(sEvent){
        this.events[sEvent.key()] = sEvent;
        this.callback();
    };

    this.removeEvent = function(key){
        var rEvent = this.events[key];
        delete this.events[key];
        this.callback();
        return rEvent;
    };

    this.getEvent = function(name, time){
        return this.events[new SingleEvent(name, time).key()];
    };

    this.key = function(){
        return this.year + ":" + this.month + ":" + this.day;
    };

    this.callback = function(){};
}

function EventManager(id, useLocalStorage){
    var mStorage = null;

    this.getLocalStorage = function(){
        return localStorage;
    };

    this.getSessionStorage = function(){
        return sessionStorage;
    };

    if(useLocalStorage){
        mStorage = new StorageManager(id, this.getLocalStorage);
    }else{
        mStorage = new StorageManager(id, this.getSessionStorage);
    }

    this.onDayModified = function(){
        this.sort();
        mStorage.syncEvent(this);
    };

    this.dayEvents = mStorage.getEvents(this.onDayModified);

    this.useLocalStorage = function(){
        mStorage.getStorage = this.getLocalStorage;
        this.dayEvents = mStorage.getEvents(this.onDayModified);
    };

    this.useSessionStorage = function(){
        mStorage.getStorage = this.getSessionStorage;
        this.dayEvents = mStorage.getEvents(this.onDayModified);
    };

    this.clearStorage = function(){
        mStorage.clear();
        this.dayEvents = {};
    };

    this.addDay = function(year, month, day){
        var dEvent = new DayEvent(year, month, day);
        dEvent.callback = this.onDayModified;
        this.dayEvents[dEvent.key()] = dEvent;
    };

    this.removeDay = function(year, month, day){
        this.dayEvents[new DayEvent(year, month, day).key()] = null;
    };

    this.hasDay = function(year, month, day){
        return this.dayEvents[new DayEvent(year, month, day).key()] != null;
    };

    this.getDay = function(year, month, day){
        return this.dayEvents[new DayEvent(year, month, day).key()];
    };
}

function EventListeners(mDate){
    this.creator = null;
    this.changer = null;

    this.setCloseOnEscape = function(form){
        document.onkeypress = function(evt) {
            evt = evt || window.event;
            if (evt.keyCode == 27) {
                __creatorReset(form);
            }
        };
    };

    this.onEventRemoved = function(form){
        var index = form.getAttribute('index');
        var dEvent = mDate.mEvent.getDay(mDate.year, mDate.month, index);
        var sEvent = dEvent.removeEvent(form.getAttribute('key'));
        mDate.writeDay(index);
        mDate.setOverflow();
        __creatorReset(form);
        mDate.onEventRemoved(sEvent);
    };

    this.onEventAdded = function(form){
        var sEvent = __createEvent(form);
        if(!mDate.mEvent.hasDay(mDate.year, mDate.month, mDate.day.value)){
            mDate.mEvent.addDay(mDate.year, mDate.month, mDate.day.value);
        }
        mDate.mEvent.getDay(mDate.year, mDate.month, mDate.day.value).addEvent(sEvent);
        mDate.writeDay(mDate.day.value);
        mDate.setOverflow();
        __creatorReset(form);
        mDate.onEventAdded(sEvent);
    };

    this.onEventChanged = function(form){
        var index = form.getAttribute('index');
        var dEvent = mDate.mEvent.getDay(mDate.year, mDate.month, index);
        dEvent.removeEvent(form.getAttribute('key'));
        var sEvent = __createEvent(form);
        dEvent.addEvent(sEvent);
        mDate.writeDay(index);
        mDate.setOverflow();
        __creatorReset(form);
        mDate.onEventChanged(sEvent);
    };

    this.setupEventForm = function(element, index){
        var sEvent = mDate.mEvent.getDay(mDate.year, mDate.month, index).events[element.getAttribute('key')];
        var form = this.changer.children[0];
        __creatorReset(form);
        __creatorReset(this.creator.children[0]);
        form.children[0].value = sEvent.name;
        form.setAttribute('key', sEvent.key());
        form.setAttribute('index', index);
        if(sEvent.meridiem != 'all'){
            var times = sEvent.time.split(':');
            var selects = form.getElementsByTagName("select");
            selects[0].value = parseInt(times[0]);
            selects[1].value = parseInt(times[1]);
            selects[2].value = times[2];
            __modTimeEnable(form);
            form.getElementsByTagName('label')[0].children[0].checked = 'true';
        }else{
            __modTimeDisable(form);
            form.getElementsByTagName('label')[1].children[0].checked = 'true';
        }
        return sEvent;
    };

    this.onEventSelected = function(element, index){
        if(window.innerWidth > Calendar.EVENT_CO_WIDTH) {
            var sEvent = this.setupEventForm(element, index);
            __moveToElement(this.changer, element.parentNode);
            if(this.creator.style.position == 'absolute'){
                this.creator.style.display = 'none';
            }
            this.setupChangeListeners("ch", this.changer, element.parentNode, this.onWindowChange);
            mDate.onEventSelected(sEvent);
        }else{
            //this.onOverflowEventSelected(element, index);
        }
    };

    this.onOverflowEventSelected = function(element, day){
        var sEvent = this.setupEventForm(element, day.value);
        __moveAbsolute(this.changer, mDate.overflowElement);
        if(this.creator.style.position == 'absolute'){
            this.creator.style.display = 'none';
        }
        this.setupChangeListeners("ch", this.changer, day.children[0], this.onOverflowWindowChange);
        mDate.onEventSelected(sEvent);
    };

    this.addEventSelected = function(element){
        if(window.innerWidth > Calendar.EVENT_CO_WIDTH){
            __creatorReset(this.creator.children[0]);
            __creatorReset(this.changer.children[0]);
            __moveToElement(this.creator, element);
            this.setupChangeListeners("cr", this.creator, element, this.onWindowChange);
        }else{
            this.onOverflowAddEventSelected(element, mDate.day);
        }
    };

    this.onOverflowAddEventSelected = function(element, day){
        __creatorReset(this.creator.children[0]);
        __creatorReset(this.changer.children[0]);
        __moveAbsolute(this.creator, mDate.overflowElement);
        this.setupChangeListeners("cr", this.creator, day.children[0], this.onOverflowWindowChange);
    };

    this.setupChangeListeners = function(key, mod, element, func){
        this.setCloseOnEscape(mod.children[0]);
        WindowManager.onWidth(mDate.id + key, func, mod, element);
    };

    this.onOverflowWindowChange = function(width, eventMod, element){
        if(eventMod.style.display != "none"){
            if(!Class.has(eventMod.children[0], 'reset')) {
                if (width <= Calendar.EVENT_WIDTH) {
                    __moveAbsolute(eventMod, mDate.overflowElement);
                } else {
                    __moveToElement(eventMod, element);
                }
            }else{
                eventMod.style.display = 'none';
            }
        }
    };

    this.onWindowChange = function(width, eventMod, element){
        if(eventMod.style.display != "none"){
            if(!Class.has(eventMod.children[0], 'reset')) {
                if (width > Calendar.EVENT_CO_WIDTH) {
                    __moveToElement(eventMod, element);
                } else {
                    __moveAbsolute(eventMod, mDate.overflowElement);
                }
            }else{
                eventMod.style.display = 'none';
            }
        }
    };
}

function DateManager(id, useLocalStorage){
    this.id = id;
    this.day = null;
    this.month = 0;
    this.year = 0;
    this.current = null;

    this.mEvent = new EventManager(id, useLocalStorage);

    this.yearSelectElement = null;
    this.monthSelectElement = null;
    this.daySelectElement = null;
    this.datesElement = null;
    this.overflowElement = null;
    this.dates = null;
    this.prevDates = null;
    this.nextDates = null;

    var eventListeners = new EventListeners(this);

    this.getEventListeners = function(){
        return eventListeners;
    };

    this.setEventListeners = function(ecr, ech){
        eventListeners.creator = ecr;
        eventListeners.changer = ech;

        eventListeners.creator.children[0].onsubmit = function(){
            if(this.children[0].value != ''){
                eventListeners.onEventAdded(this);
            }
            return false;
        };

        eventListeners.changer.children[0].onsubmit = function(){
            if(this.children[0].value != ''){
                eventListeners.onEventChanged(this);
            }
            return false;
        };

        eventListeners.changer.children[0].getElementsByTagName("button")[2].onclick = function(){
            eventListeners.onEventRemoved(this.parentNode);
        };
    };

    this.writeDayForElement = function(element, year, month, day, editable){
        element.innerHTML = "";

        if(this.mEvent.hasDay(year, month, day)) {
            var dEvent = this.mEvent.getDay(year, month, day);
            for (var key in dEvent.events) {
                if (dEvent.events.hasOwnProperty(key)) {
                    if (dEvent.events[key] != null) {
                        element.innerHTML += __getEventHtml(key, dEvent.events[key]);
                    }
                }
            }
            if(editable){
                for (var i = 0; i < element.children.length; i++) {
                    element.children[i].onclick = function () {
                        eventListeners.onEventSelected(this, day);
                    };
                }
            }
        }
    };

    this.writeDayForPrev = function(year, month, index){
        this.writeDayForElement(this.prevDates[index - 1].children[1], year, month, this.prevDates[index - 1].value, false);
    };

    this.writeDayForNext = function(year, month, index){
        this.writeDayForElement(this.nextDates[index - 1].children[1], year, month, this.nextDates[index - 1].value, false);
    };

    this.writeDay = function(index){
        this.writeDayForElement(this.dates[index - 1].children[1], this.year, this.month, index, true);
    };

    this.isMonth = function(year, month){
        return (year == this.current.year && month == this.current.month);
    };

    this.setOverflow = function(){
        this.overflowElement.innerHTML = this.day.innerHTML;
        this.overflowElement.children[0].innerHTML = Calendar.MONTHS[this.month] + '&nbsp;' + this.overflowElement.children[0].innerHTML;
        this.overflowElement.children[1].innerHTML += '<div class="cal-event-add">Add</div>';
        var day = this.day;
        for(var i=0; i<this.overflowElement.children[1].children.length-1; i++){
            this.overflowElement.children[1].children[i].onclick = function(){
                eventListeners.onOverflowEventSelected(this, day);
            };
        }
        this.overflowElement.children[1].children[this.overflowElement.children[1].children.length-1].onclick = function(){
            eventListeners.onOverflowAddEventSelected(this, day);
        };
    };

    this.set = function(year, month, day){
        this.setYear(year);
        this.setMonth(month);
        this.setDayByDate(day);
    };

    this.setDayByDate = function(date){
        this.setDayByElement(this.dates[date - 1]);
    };

    this.setDayByElement = function(element){
        if(this.day != element) {
            if (this.day != null) {
                Class.remove(this.day, "selected");
            }
            this.day = element;
            Class.add(this.day, "selected");
            this.daySelectElement.selectedIndex = parseInt(this.day.value) - 1;
            this.setOverflow();
            if(eventListeners.creator.style.display == 'block' && !Class.has(eventListeners.creator.children[0], 'reset')){
                eventListeners.addEventSelected(element.children[0]);
            }else if(eventListeners.changer.style.display == 'block' && eventListeners.changer.style.position != 'absolute'){
                __creatorReset(eventListeners.changer.children[0]);
            }
            this.onDateSelected(new DateObject(this.id, this.year, this.month, this.day.value));
        }
    };

    this.setMonth = function(month){
        __creatorReset(eventListeners.changer.children[0]);
        var monthInfo = new MonthInfo(this.year, month);
        this.month = monthInfo.month;
        if(this.year != monthInfo.year){
            this.setYear(monthInfo.year);
        }
        this.monthSelectElement.selectedIndex = this.month - 1;
        var date = 1;
        if(this.day != null){
            date = parseInt(this.day.value);
            if(date > monthInfo.numDays){
                date = monthInfo.numDays;
            }
        }
        this.daySelectElement.innerHTML = __getCalendarDayOptions(monthInfo.numDays);
        this.datesElement.innerHTML = __getCalendarDates(monthInfo.firstPosition, monthInfo.numDays, monthInfo.numDaysPrevious);
        this.triggers();
        this.setDayByDate(date);
        if(this.isMonth(this.year, this.month)){
            Class.add(this.dates[this.current.day - 1], "today");
        }
        for(var i=1; i<=this.dates.length; i++){
            this.writeDay(i);
        }
        monthInfo = new MonthInfo(this.year, this.month - 1);
        for(i=1; i<=this.prevDates.length; i++){
            this.writeDayForPrev(monthInfo.year, monthInfo.month, i);
        }
        monthInfo = new MonthInfo(this.year, this.month + 1);
        for(i=1; i<=this.nextDates.length; i++){
            this.writeDayForNext(monthInfo.year, monthInfo.month, i);
        }
        this.setOverflow();
    };

    this.setYear = function(year){
        this.year = year;
        this.yearSelectElement.innerHTML = __getCalendarYearOptions(this.year);
    };

    this.onDateSelected = function(object){};
    this.onEventAdded = function(object){};
    this.onEventChanged = function(object){};
    this.onEventSelected = function(object){};
    this.onEventRemoved = function(object){};
}

function CalendarObject(id, useLocalStorage){
    this.element = document.getElementById(id);
    this.monthLeft = null;
    this.monthRight = null;
    var mDate = new DateManager(id, useLocalStorage);

    this.useLocalStorage = function(){
        mDate.mEvent.useLocalStorage();
        mDate.setMonth(mDate.month);
    };

    this.useSessionStorage = function(){
        mDate.mEvent.useSessionStorage();
        mDate.setMonth(mDate.month);
    };

    this.clear = function(){
        mDate.mEvent.clearStorage();
        mDate.setMonth(mDate.month);
    };

    this.getEvents = function(){
        return mDate.mEvent.dayEvents;
    };

    this.getEventsAsString = function(){
        return JSON.stringify(mDate.mEvent.dayEvents);
    };

    this.getEventsFor = function(year, month, day){
        if(!mDate.mEvent.hasDay(year, month, day)){
            return mDate.mEvent.getDay(year, month, day).events;
        }
        return null;
    };

    this.addEvent = function(name, time, year, month, day){
        var sEvent = new SingleEvent(name, time);
        if(!mDate.mEvent.hasDay(year, month, day)){
            mDate.mEvent.addDay(year, month, day);
        }
        mDate.mEvent.getDay(year, month, day).addEvent(sEvent);
        if(mDate.isMonth(year, month)){
            mDate.writeDay(day);
        }
    };

    this.removeEvent = function(name, time, year, month, day){
        if(!mDate.mEvent.hasDay(year, month, day)){
            mDate.mEvent.getDay(year, month, day).removeEvent(new SingleEvent(name, time).key());
        }
    };

    this.logEvents = function(){
        for (var key in mDate.mEvent.dayEvents) {
            if (mDate.mEvent.dayEvents.hasOwnProperty(key)) {
                console.log(key + " -> " + mDate.mEvent.dayEvents[key]);
                for (var key2 in mDate.mEvent.dayEvents[key].events) {
                    if (mDate.mEvent.dayEvents[key].events.hasOwnProperty(key2)) {
                        console.log(key2 + " -> " + mDate.mEvent.dayEvents[key].events[key2]);
                    }
                }
            }
        }
    };

    this.setOnDateSelected = function(func){
        mDate.onDateSelected = func;
    };

    this.setOnEventAdded = function(func){
        mDate.onEventAdded = func;
    };

    this.setOnEventChanged = function(func){
        mDate.onEventChanged = func;
    };

    this.setOnEventSelected = function(func){
        mDate.onEventSelected = func;
    };

    this.setOnEventRemoved = function(func){
        mDate.onEventRemoved = func;
    };

    this.initCalendar = function(){
        var html = "<div class='cal-wrap'>";
        html += __getCalendarNav();
        html += __getCalendarHeaders() + '<div class="cal-dates"></div>';
        html += __getEventCreator();
        html += __getEventChanger();
        html += "<div class='cal-overflow'><div></div></div>";
        this.element.innerHTML = html + "</div>";

        mDate.yearSelectElement = this.element.getElementsByClassName("cal-select-year")[0];
        mDate.monthSelectElement = this.element.getElementsByClassName("cal-select-month")[0];
        mDate.daySelectElement = this.element.getElementsByClassName("cal-select-day")[0];

        mDate.datesElement = this.element.getElementsByClassName("cal-dates")[0];

        mDate.overflowElement = this.element.getElementsByClassName("cal-overflow")[0].children[0];

        var ecr = this.element.getElementsByClassName("cal-event-mod create")[0];
        var ech = this.element.getElementsByClassName("cal-event-mod change")[0];

        mDate.setEventListeners(ecr, ech);

        var arrows = this.element.getElementsByClassName('cal-nav')[0].getElementsByTagName('button');
        this.monthLeft = arrows[0];
        this.monthRight = arrows[1];

        mDate.daySelectElement.onchange=function(){
            mDate.setDayByDate(__getSelectedValue(this));
        };

        mDate.monthSelectElement.onchange=function(){
            mDate.setMonth(__getSelectedValue(this));
        };

        mDate.yearSelectElement.onchange=function(){
            mDate.setYear(__getSelectedValue(this));
            mDate.setMonth(mDate.month);
        };

        this.monthLeft.onclick = function(){
            mDate.setMonth(mDate.month - 1);
        };

        this.monthRight.onclick = function(){
            mDate.setMonth(mDate.month + 1);
        };

        var cur = new Date();
        mDate.current = new DateObject(id, cur.getFullYear(), cur.getMonth()+1, cur.getDate());
        mDate.set(cur.getFullYear(), cur.getMonth()+1, cur.getDate());

        return this;
    };

    mDate.triggers = function(){
        mDate.dates = [];
        mDate.prevDates = [];
        mDate.nextDates = [];
        var elements = mDate.datesElement.getElementsByTagName("li");
        for(var i = 0; i < elements.length; i++){
            var name = elements[i].getAttribute("name");
            if(name == "cal-on"){
                mDate.dates.push(elements[i]);
            }else if(name == "cal-off-l"){
                mDate.prevDates.push(elements[i]);
            }else if(name == "cal-off-r"){
                mDate.nextDates.push(elements[i]);
            }
        }
        for (i = 0; i < mDate.dates.length; i++) {
            mDate.dates[i].onclick=function(){
                mDate.setDayByElement(this);
            };
            mDate.dates[i].ondblclick=function(){
                mDate.getEventListeners().addEventSelected(this.children[0]);
            };

        }

        for (i = 0; i < mDate.prevDates.length; i++) {
            mDate.prevDates[i].onclick=function(){
                mDate.setMonth(mDate.month - 1);
                mDate.setDayByDate(this.value);
            };
        }

        for (i = 0; i < mDate.nextDates.length; i++) {
            mDate.nextDates[i].onclick=function(){
                mDate.setMonth(mDate.month + 1);
                mDate.setDayByDate(this.value);
            };
        }
    };

}

var Calendar = new function(){
    this.EVENT_CO_WIDTH = 700;
    this.EVENT_WIDTH = 700;
    this.YEAR_RANGE = 5;
    this.WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat"];
    this.MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

    this.create = function(id, useLocalStorage){
        if(useLocalStorage == null){
            useLocalStorage = false;
        }
        return new CalendarObject(id, useLocalStorage).initCalendar();
    };

};

function __getCalendarNav(){
    var calNav = "<div class='cal-nav'><div class='cal-nav-wrap'>";
    calNav += "<button>&nbsp;&nbsp;&nbsp;&#8592;&nbsp;&nbsp;&nbsp;</button>";
    calNav += __getCalendarDaySelect();
    calNav += __getCalendarMonthSelect();
    calNav += __getCalendarYearSelect();
    calNav += "<button>&nbsp;&nbsp;&nbsp;&#8594;&nbsp;&nbsp;&nbsp;</button>";
    return calNav + "</div></div>";
}

function __getCalendarDaySelect(){
    return "<select class='cal-select-day'></select>";
}

function __getCalendarDayOptions(days){
    var options = '';
    for(var i = 1; i <= days; i++){
		options += "<option value='" + i + "'>" + i + "</option>";
    }
    return options;
}

function __getCalendarMonthSelect() {
	var select = "<select class='cal-select-month'>";
    select += __getCalendarMonthOptions();
    return select + "</select>";
}

function __getCalendarMonthOptions(){
    var options = '';
    for(var i = 1; i < Calendar.MONTHS.length; i++) {
		options += "<option value=" + i + ">" + Calendar.MONTHS[i] + "</option>";
	}
    return options;
}

function __getCalendarYearSelect() {
	return "<select class='cal-select-year'></select>";
}

function __getCalendarYearOptions(year){
    year = parseInt(year);
    var options = '';
    for(var i=year-Calendar.YEAR_RANGE; i<=year+Calendar.YEAR_RANGE; i++){
		if(i==year){
			options += "<option selected value='" + i + "'>" + i + "</option>";
		}else{
			options += "<option value='" + i + "'>" + i + "</option>";
		}
	}
    return options;
}

function __getCalendarHeaders(){
    var header = "<li class='border-left'>" + Calendar.WEEKDAYS[0] + "</li>";
    for(var i = 1; i < 7; i++){
        header += "<li>" + Calendar.WEEKDAYS[i] + "</li>";
    }
    return '<div class="cal-headers"><ol>' + header + '</ol></div>';
}

function __getCalendarDates(firstPosition, numDays, numDaysPrevious){
    var pos = firstPosition;
    var lDays = numDaysPrevious - pos + 1;
    var text = "<ol>";
    var count = 0;

    for(var i = 0; i < pos; i++){
        count += 1;
        if(i === 0){
            text += "<li name='cal-off-l' value='" + (lDays + i) + "' class='border-left'><div class='cal-date-num'>" + (lDays + i) + "</div><div class='cal-event-holder'></div></li>";
        }else {
            text += "<li name='cal-off-l' value='" + (lDays + i) + "'><div class='cal-date-num'>" + (lDays + i) + "</div><div class='cal-event-holder'></div></li>";
        }
    }
    
    for(i = 1; i <= numDays; i++){
        count += 1;
        if (pos === 0 && text !== "") {
            if(i > 1) {
                text += "</ol><ol>";
            }
        }

        if(pos === 0){
            text += "<li name='cal-on' value='" + i + "' class='border-left'><div class='cal-date-num'>" + i + "</div><div class='cal-event-holder'></div></li>";
        }else{
            text += "<li name='cal-on' value='" + i + "'><div class='cal-date-num'>" + i + "</div><div class='cal-event-holder'></div></li>";
        }
        pos = (pos + 1) % 7;
    }

    var c = 1;
    if (count < 42){
	    for(i = count; i < 42; i++){
            if(pos == 0) {
                text += '</ol><ol>';
                text += "<li class='border-left' name='cal-off-r' value='" + c + "'><div class='cal-date-num'>" + c + "</div><div class='cal-event-holder'></div></li>";
            }else{
                text += "<li name='cal-off-r' value='" + c + "'><div class='cal-date-num'>" + c + "</div><div class='cal-event-holder'></div></li>";
            }
	        c += 1;
            pos = (pos + 1) % 7;
	    }
    }

    return text + "</ol>";
}

function __zeroFill(num, minDigits){
    num = num.toString();
    while(num.length < minDigits){
        num = "0" + num;
    }
    return num;
}

function __dynamicSort(property){
    var sortOrder = 1;
    if(property[0] === "-") {
        sortOrder = -1;
        property = property.substr(1);
    }
    return function (a,b) {
        var result = (a[property] < b[property]) ? -1 : (a[property] > b[property]) ? 1 : 0;
        return result * sortOrder;
    }
}

function __getNumberPicker(top, bottom, selected, minDigits){
    var html = '<select>';
    var min = top % bottom;
    if (min < top){
        html += '<option value="' + top + '" ';
        if(top == selected){
            html += 'selected';
        }
        top = __zeroFill(top, minDigits);
        html += '>' + top.toString() + '</option>';
    }
    for(var i=min; i<=bottom; i++){
        html += '<option value="' + i + '" ';
        if(i == selected){
            html += 'selected';
        }
        var v = __zeroFill(i, minDigits);
        html += '>' + v + '</option>';
    }
    return html + '</select>';
}

function __getEventCreator(){
    var html = '<div class="cal-event-mod create">';
    html += '<form time="spec">';
    html += '<input type="text" name="name" placeholder="New Event">';
    html += '<label>Time:<input type="radio" name="time" value="time" onclick="__modTimeEnable(this.parentNode.parentNode);" checked></label>';
    html += '<label>All Day:<input type="radio" name="time" value="all" onclick="__modTimeDisable(this.parentNode.parentNode);"></label><br>';
    html += __getNumberPicker(12, 11, 9, 1);
    html += __getNumberPicker(0, 59, 0, 2);
    html += '<select><option>AM</option><option>PM</option></select>';
    html += '<a class="new-line">&nbsp;</a>';
    html += '<button type="submit">Add</button>';
    html += '<button type="button" onclick="__creatorReset(this.parentNode);">Cancel</button>';
    html += '</form>';
    return html + '</div>';
}

function __modAnimate(form, animate){
    if(animate){
        Class.remove(form, 'no-trans');
        Class.add(form, 'shift');
    }else{
        Class.add(form, 'no-trans');
        Class.remove(form, 'shift');
    }
}

function __creatorReset(form){
    var inputs = form.getElementsByTagName("input");
    inputs[0].value = '';

    Class.add(form, 'reset');
    Class.remove(form, 'shift');

    if(form.parentNode.style.position == 'absolute') {
        form.parentNode.style.display = 'none';
    }
    /*
    if(Class.has(form, 'shift')){
        setTimeout(function(){
            Class.remove(form, 'shift');
        }, 100);
    }
    */
}

function __modTimeEnable(form){
    var selects = form.getElementsByTagName("select");
    for(var i = 0; i < selects.length; i++){
        selects[i].removeAttribute('disabled');
    }
    form.setAttribute('time', 'spec');
}

function __modTimeDisable(form){
    var selects = form.getElementsByTagName("select");
    for(var i = 0; i < selects.length; i++){
        selects[i].setAttribute('disabled', 'true');
    }
    form.setAttribute('time', 'all');
}

function __getEventChanger(){
    var html = '<div class="cal-event-mod change">';
    html += '<form time="spec">';
    html += '<input type="text" name="name">';
    html += '<label>Time:<input type="radio" name="time" value="time" onclick="__modTimeEnable(this.parentNode.parentNode);" checked></label>';
    html += '<label>All Day:<input type="radio" name="time" value="all" onclick="__modTimeDisable(this.parentNode.parentNode);"></label><br>';
    html += __getNumberPicker(12, 11, 9, 1);
    html += __getNumberPicker(0, 59, 0, 2);
    html += '<select><option>AM</option><option>PM</option></select>';
    html += '<a class="new-line">&nbsp;</a>';
    html += '<button type="submit">Change</button>';
    html += '<button type="button" onclick="__creatorReset(this.parentNode);">Cancel</button>';
    html += '<button class="cal-right" type="button">Remove</button>';
    html += '</form>';
    return html + '</div>';
}

function __getEventHtml(key, sEvent){
    var minute = " ";
    if(sEvent.minute != 0){
        minute = ":" + __zeroFill(sEvent.minute, 2) + " ";
    }
    return "<div key='" + Replace.quote(key) + "'><div class='cal-left'>" + sEvent.name + "</div><div class='cal-right'>" + sEvent.timeFormat + "</div></div>";
}

function __createEvent(form){
    var time = form.getAttribute('time');
    var h = 0;
    var m = 0;
    var ap = 'all';
    if(time != 'all') {
        var timeSelect = form.getElementsByTagName("select");
        h = __getSelectedValue(timeSelect[0]);
        m = __getSelectedValue(timeSelect[1]);
        ap = __getSelectedValue(timeSelect[2]);
    }
    var name = form.getElementsByTagName("input")[0].value;
    return new SingleEvent(name, __zeroFill(h, 2) + ':' + __zeroFill(m, 2) + ':' + ap);
}

function __getSelectedValue(select){
    return select.options[select.selectedIndex].value;
}

function __moveAbsolute(elementFrom, elementTo) {
    elementFrom.style.zIndex = "2";
    elementFrom.style.left = "0";
    elementFrom.style.right = "0";
    elementFrom.style.top = "initial";
    elementFrom.style.bottom = "initial";
    elementFrom.style.position = "fixed";
    elementFrom.style.display = "block";
    var height = elementFrom.getBoundingClientRect().height;
    elementFrom.style.marginTop = "-" + height + "px";
    elementFrom.style.position = "relative";
    __modAnimate(elementFrom.children[0], true);
    Class.remove(elementFrom.children[0], 'reset');
}

function __moveToElement(elementFrom, elementTo){
    __modAnimate(elementFrom.children[0], false);
    elementFrom.style.zIndex = "initial";
    elementFrom.style.marginTop = "initial";
    elementFrom.style.top = "0";
    elementFrom.style.left = "0";
    elementFrom.style.right = "initial";
    elementFrom.style.bottom = "initial";
    elementFrom.style.position = "fixed";
    elementFrom.style.display = "block";
    var bound = elementTo.parentNode.getBoundingClientRect();
    var ecBound = elementFrom.getBoundingClientRect();
    var width = (ecBound.right - ecBound.left);
    var height = (ecBound.bottom - ecBound.top);

    var left = bound.right + window.scrollX;
    if(left + width > window.innerWidth){
        left = bound.left + window.scrollX - width;
    }

    var top = bound.top + window.scrollY;
    if(top + height > window.innerHeight){
        top = bound.bottom + window.scrollY - height;
    }

    elementFrom.style.top = top + "px";
    elementFrom.style.left = left + "px";
    elementFrom.style.position = "absolute";
    Class.remove(elementFrom.children[0], 'reset');
}


var Replace = new function(){
    this.__quotes = {'\'': '&#39;', '"': '&#34;'};

    this.quote = function(str){
        for(var key in this.__quotes){
            str = this.all(str, key, this.__quotes[key]);
        }
        return str;
    };

    this.encode = function(str){
        return encodeURI(str);
    };

    this.all = function(str, find, replace){
        return str.replace(new RegExp(find, 'g'), replace);
    };
};

var Class = new function(){
    this.has = function(element, cls){
        return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
    };

    this.remove = function(element, cls){
        if(Class.has(element, cls)) element.className = element.className.replace(cls, '').trim();
    };

    this.add = function(element, cls) {
        if (!Class.has(element, cls)) {
            if (element.className == '') element.className = cls;
            else element.className += (' ' + cls);
        }
    };

    this.toggle = function(element, cls){
        if(Class.has(element, cls)){
            Class.remove(element, cls); return false;
        }else{
            Class.add(element, cls); return true;
        }
    };

    this.set = function(id, cls){
        document.getElementById(id).className = cls;
    };
};