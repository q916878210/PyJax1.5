var Toggle = new function(){
    var fn = new function(){
        this.getHtml = function(){
            var html = '<div class="toggle-label-wrap">';
            html += '<span></span><span></span>';
            html += '</div>';
            html += '<div class="toggle-switch"></div>';
            return html;
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

        this.cls = cls;
    };

    var ToggleObject = function(parent, func){
        this.element = document.createElement('div');
        this.labelElements = null;

        var toggleButton = null;
        var toggled = false;
        var element = this.element;

        this.toggle = function(){
            var status = fn.cls.toggle(element, 'shift');

            if(func){
                func(status);
            }
            parent.setAttribute('checked', status);
        };

        this.init = function(){
            this.element.className = 'toggle';
            this.element.innerHTML = fn.getHtml();
            parent.appendChild(this.element);

            this.labelElements = this.element.getElementsByTagName('span');
            this.labelElements[0].innerText = 'on';
            this.labelElements[1].innerText = 'off';

            var labelWrap = this.element.getElementsByClassName('toggle-label-wrap')[0];

            this.element.onclick = this.toggle;

            return this;
        };
    };

    this.make = function(element, func){
        return new ToggleObject(element, func).init();
    };
};