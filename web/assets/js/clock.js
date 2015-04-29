var Clock = new function(){
    var fn = new function(){
        this.setupClock = function(elements, cv, cx, cy, r, o){
            var div = 360 / Object.keys(elements).length;
            var off = (90 / div) - o;
            var index = 0;
            for(var key in elements){
                var angle = ((index - off) * div) * cv;
                var xp = cx + (r * Math.cos(angle));
                var yp = cy + (r * Math.sin(angle));
                elements[key].style.left = xp + "px";
                elements[key].style.top = yp + "px";
                index++;
            }
        };

        this.getDialogButton = function(){
            var html = '<button>Clock</button>';
            return html;
        };

        this.getClockDisplay = function(){
            var html = '<div class="clock-display"><div>';
            html += '<a class="selected">0</a>';
            html += '<a>:</a>';
            html += '<a>00</a>';
            html += '<a>am</a>';
            return html + '</div></div>';
        };

        this.getClockNumbers = function(){
            var html = '<div class="clock-numbers"><div>';
            for(var i=1; i<=12; i++){
                html += '<div><a>' + i + '</a></div>';
            }
            html += '</div><div class="hide">';
            for(i=0; i<12; i++){
                html += '<div><a>' + this.zeroFill(i*5, 2) + '</a></div>';
            }

            return html + '</div></div>';
        };

        this.getClockPickerM = function(){
            var html = '<div class="clock-pick-m">';
            html += '<a class="selected">am</a><a>pm</a>';
            return html + '</div>';
        };

        this.getClockBottom = function(){
            var html = '<div class="clock-bottom hide"><hr><button>Done</button></div>';
            return html;
        };

        this.zeroFill = function(num, minDigits){
            num = num.toString();
            while(num.length < minDigits){
                num = "0" + num;
            }
            return num;
        };

        var ease = function(time){
            return time < 0.5 ? 4 * time * time * time : (time - 1) * (2 * time - 2) * (2 * time - 2) + 1;
        };

        this.animate = function(start, stop, time, func1, func2){
            var c = start < stop ? 1 : -1;
            var end = start < stop ? ease(stop): ease(start);
            time = time / Math.abs(stop - start);
            var i = setInterval(function(){
                func1(((ease(start) / end) * start).toFixed(2));
                if(start == stop){
                    clearInterval(i);
                    func2();
                }else{
                    start += c;
                }
            }, time);
        };
    };

    var cls = new function(){
        this.has = function(element, name){
            return (' ' + element.className + ' ').indexOf(' ' + name + ' ') > -1;
        };

        this.remove = function(element, name){
            if(cls.has(element, name)){
                if (element.className.indexOf(' ' + name) > -1){
                    element.className = element.className.replace(' ' + name, '').trim();
                }else{
                    element.className = element.className.replace(name, '').trim();
                }
            }
        };

        this.add = function(element, name) {
            if (!cls.has(element, name)) {
                if (element.className == '') element.className = name;
                else element.className += (' ' + name);
            }
        };

        this.toggle = function(element, name){
            if(cls.has(element, name)){
                cls.remove(element, name); return false;
            }else{
                cls.add(element, name); return true;
            }
        };
    };

    function TimeObject(hour, minute, meridian){
        this.hour = hour;
        this.minute = minute;
        this.meridian = meridian;
        this.asString = function(){
            return this.hour + ':' + this.minute + ' ' + this.meridian;
        }
    }

    function FunctionList(){
        this.functions = [];

        this.add = function(func){
            this.functions.push(func);
        };

        this.execute = function(item){
            for(var i=0; i<this.functions.length; i++){
                this.functions[i](item);
            }
        };
    }

    function FunctionManager(){
        this.functionMap = {};

        this.getFunctionList = function(name){
            if(this.functionMap[name] == null){
                this.functionMap[name] = new FunctionList();
            }
            return this.functionMap[name];
        };

        this.add = function(name, func){
            this.getFunctionList(name).add(func);
        };

        this.trigger = function(name, item){
            if(this.functionMap[name] != null){
                this.functionMap[name].execute(item);
            }
        };
    }

    function ClockManager(id){
        this.id = id;
        this.displayTime = null;
        this.displayUM = null;
        this.selectedHour = null;
        this.selectedMinute = null;
        this.hours = {};
        this.minutes = {};
        this.hourHolder = null;
        this.minuteHolder = null;
        this.bottom = null;

        this.getVisibleHolder = function(){
            if(cls.has(this.hourHolder, 'hide')) return this.minuteHolder;
            else return this.hourHolder;
        };

        this.getTime = function(){
            return new TimeObject(this.selectedHour.innerText, this.selectedMinute.innerText, this.displayUM.innerText);
        };

        this.setTime = function(hour, min){
            this.setHour(hour);
            this.setMinute(min);
        };

        this.selectUM = function(value){
            if(value == 'am'){
                this.displayUM.innerText = 'am';
                cls.remove(this.bottom[1], 'selected');
                cls.add(this.bottom[0], 'selected');
            }else{
                this.displayUM.innerText = 'pm';
                cls.remove(this.bottom[0], 'selected');
                cls.add(this.bottom[1], 'selected');
            }
            this.onMeridianSelected(this.displayUM.innerText);
            this.onChange();
        };

        this.toggleUM = function(value){
            value == 'am' ? this.selectUM('pm'): this.selectUM('am');
        };

        this.setHour = function(value){
            this.selectHour(this.hours[value]);
        };

        this.selectHour = function(element){
            if(this.selectedHour != null){
                cls.remove(this.selectedHour, 'selected');
            }
            cls.add(element, 'selected');
            this.selectedHour = element;
            this.displayTime[0].innerText = this.selectedHour.innerText;
            this.onHourSelected(this.selectedHour.innerText);
            this.onChange();
        };

        this.setMinute = function(value){
            this.selectMinute(this.minutes[fn.zeroFill(value, 2)]);
        };

        this.selectMinute = function(element){
            if(this.selectedMinute != null){
                cls.remove(this.selectedMinute, 'selected');
            }
            cls.add(element, 'selected');
            this.selectedMinute = element;
            this.displayTime[2].innerText = this.selectedMinute.innerText;
            this.onMinuteSelected(this.selectedMinute.innerText);
            this.onChange();
        };

        this.displayHours = function(){
            cls.remove(this.displayTime[2], 'selected');
            cls.add(this.displayTime[0], 'selected');
            cls.remove(this.hourHolder, 'hide');
            cls.add(this.minuteHolder, 'hide');
        };

        this.displayMinutes = function(){
            cls.remove(this.displayTime[0], 'selected');
            cls.add(this.displayTime[2], 'selected');
            cls.remove(this.minuteHolder, 'hide');
            cls.add(this.hourHolder, 'hide');
        };

        this.onHourSelected = function(value){};
        this.onMinuteSelected = function(value){};
        this.onMeridianSelected = function(value){};
        this.onChange = function(){};
    }

    function ClockObject(id){

        this.id = id;
        var cm = new ClockManager(id);
        var functionManager = new FunctionManager();
        var element = document.createElement('div');
        this.element = element;
        this.dialogButton = null;
        this.doneButton = null;

        this.onChange = function(){
            functionManager.trigger('change');
        };

        this.setOnChange = function(func){
            functionManager.add('change', func);
        };

        this.getTime = function(){
            return cm.getTime();
        };

        this.setOnDialog = function(func){
            this.onDialog = func;
        };

        this.setOnHourSelected = function(func){
            cm.onHourSelected = func;
        };

        this.setOnMinuteSelected = function(func){
            cm.onMinuteSelected = func;
        };

        this.setOnMeridianSelected = function(func){
            cm.onMeridianSelected = func;
        };

        this.show = function(){
            cls.remove(element, 'hide');
            this.position();
            this.onDialog(true);
        };

        this.hide = function(){
            cls.add(element, 'hide');
            this.onDialog(false);
        };

        this.toggle = function(){
            if(cls.has(this.element, 'hide')){
                this.show();
            }else{
                this.hide();
            }
        };

        this.onDialog = function(show){};

        this.position = function(){
            var bounds = cm.getVisibleHolder().getBoundingClientRect();

            var cv = Math.PI / 180;
            var cx = (bounds.right - bounds.left - 26) / 2;
            var cy = (bounds.bottom - bounds.top - 26) / 2;
            var r = (bounds.width - 31) / 2;

            fn.setupClock(cm.hours, cv, cx, cy, r, 1);
            fn.setupClock(cm.minutes, cv, cx, cy, r, 2);
        };

        this.init = function(className){
            var html = fn.getClockDisplay();
            html += fn.getClockNumbers();
            html += fn.getClockPickerM();
            html += fn.getClockBottom();
            cls.add(this.element, 'clock-wrap');
            if(className != null){
                cls.add(this.element, className);
            }

            if(cls.has(this.element, 'dialog')){
                var clockWrapper = document.createElement('div');
                cls.add(clockWrapper, 'clock-dialog-wrap');
                var dialog = document.getElementById(this.id);
                dialog.parentNode.insertBefore(clockWrapper, dialog.nextSibling);
                dialog.parentNode.removeChild(dialog);
                clockWrapper.appendChild(dialog);
                clockWrapper.appendChild(this.element);
            }else{
                document.getElementById(this.id).appendChild(this.element);
            }
            this.element.innerHTML = html;

            var display = this.element.getElementsByClassName('clock-display')[0];
            cm.displayTime = display.getElementsByTagName('a');
            cm.displayUM = cm.displayTime[3];

            var numberHolder = this.element.getElementsByClassName('clock-numbers')[0];

            cm.hourHolder = numberHolder.children[0];
            cm.minuteHolder = numberHolder.children[1];

            for(var i=0; i<cm.hourHolder.children.length; i++){
                cm.hours[cm.hourHolder.children[i].innerText] = cm.hourHolder.children[i];
                cm.hourHolder.children[i].onclick = function(){
                    cm.selectHour(this);
                };
            }

            for(i=0; i<cm.minuteHolder.children.length; i++){
                cm.minutes[cm.minuteHolder.children[i].innerText] = cm.minuteHolder.children[i];
                cm.minuteHolder.children[i].onclick = function(){
                    cm.selectMinute(this);
                };
            }

            cm.bottom = this.element.getElementsByClassName('clock-pick-m')[0].getElementsByTagName('a');
            this.doneButton = this.element.getElementsByClassName('clock-bottom')[0];

            cm.displayTime[0].onclick = function(){
                cm.displayHours();
            };

            cm.displayTime[2].onclick = function(){
                cm.displayMinutes();
            };

            cm.displayUM.onclick = function(){
                cm.toggleUM(this.innerText);
            };

            for(i=0; i<cm.bottom.length; i++){
                cm.bottom[i].onclick = function(){
                    cm.selectUM(this.innerText);
                };
            }

            if(className != 'hide'){
                this.position();
                cm.setTime(9, 0);
            }

            cm.onChange = this.onChange;

            return this;
        };
    }

    this.create = function(id){
        return new ClockObject(id).init();
    };

    this.dialog = function(id){
        var __clock = new ClockObject(id).init('hide dialog');
        __clock.dialogButton = document.getElementById(id);
        if(__clock.dialogButton.tagName == 'INPUT'){
            __clock.dialogButton.setAttribute('readonly', 'readonly');
            __clock.dialogButton.onclick = function(){
                __clock.toggle();
            };
            __clock.setOnChange(function(){
                __clock.dialogButton.value = __clock.getTime().asString();
            });

            cls.remove(__clock.doneButton, 'hide');

            __clock.doneButton.onclick = function(){
                __clock.onChange();
                __clock.hide();
            };

        }else{
            __clock.dialogButton.onclick = function(){
                __clock.toggle();
            };
        }

        return __clock;
    };

};