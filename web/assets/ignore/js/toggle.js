/**
 * Created by seanmead on 4/14/15.
 */


var Toggle = new function(){
    var getToggleHtml = function(){
        var html = '<div class="toggle-label-wrap">';
        html += '<span></span><span></span>';
        html += '</div>';
        html += '<div class="toggle-switch"></div>';
        return html;
    };

    var hasClass = function(element, cls){
        return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
    };

    var removeClass = function(element, cls){
        if(hasClass(element, cls)){
            if (element.className.indexOf(' ' + cls) > -1){
                element.className = element.className.replace(' ' + cls, '').trim();
            }else{
                element.className = element.className.replace(cls, '').trim();
            }
        }
    };

    var addClass = function(element, cls) {
        if (!hasClass(element, cls)) {
            if (element.className == '') element.className = cls;
            else element.className += (' ' + cls);
        }
    };

    var toggleClass = function(element, cls){
        if(hasClass(element, cls)){
            removeClass(element, cls); return false;
        }else{
            addClass(element, cls); return true;
        }
    };

    var ToggleObject = function(id, func){
        var parent = document.getElementById(id);

        this.element = document.createElement('div');
        this.labelElements = null;

        var toggleButton = null;
        var toggled = false;
        var element = this.element;

        this.toggle = function(){
            var status = toggleClass(element, 'shift');
            if(func){
                func(status);
            }
            parent.setAttribute('checked', status);
        };

        this.init = function(){
            this.element.className = 'toggle';
            this.element.innerHTML = getToggleHtml();
            parent.appendChild(this.element);

            this.labelElements = this.element.getElementsByTagName('span');
            this.labelElements[0].innerText = 'on';
            this.labelElements[1].innerText = 'off';

            var labelWrap = this.element.getElementsByClassName('toggle-label-wrap')[0];

            this.element.onclick = this.toggle;


            return this;
        };
    };

    this.create = function(id, func){
        return new ToggleObject(id, func).init();
    };

};