/**
 * Created by seanmead on 4/27/15.
 */

var Swipe = new function(){

    var SwipeEvent = function(tObj){
        this.width = 0;
        this.height = 0;
        this.elapse = 0;
        this.xDir = 0;
        this.yDir = 0;
        var x = tObj.pageX;
        var y = tObj.pageY;
        var start = new Date().getTime();

        this.onEnd = function(tObj){
            this.elapse = new Date().getTime() - start;
            this.width = Math.abs(tObj.pageX - x);
            this.height = Math.abs(tObj.pageY - y);
            this.xDir = tObj.pageX > x ? 1: -1;
            this.yDir = tObj.pageY > y ? -1: 1;
        };
    };

    var SwipePane = function(element, speed, ph, pw){
        var bounds = element.getBoundingClientRect();
        var maxHeight = bounds.height;
        var maxWidth = bounds.width;

        var minHeight = maxHeight / ph;
        var minWidth = maxWidth / pw;

        this.up = function(){};

        this.down = function(){};

        this.right = function(){};

        this.left = function(){};

        var handle = function(a, cEvent){
            var inY = cEvent.height <= maxHeight;
            var inX = cEvent.width <= maxWidth;

            var tX = cEvent.width >= minWidth;
            var tY = cEvent.height >= minHeight;
            var t = cEvent.elapse <= speed;

            if(t && inY && inX){
                if(tX){
                    cEvent.xDir == 1 ? a.right() : a.left();
                }else if(tY){
                    cEvent.yDir == 1 ? a.up() : a.down();
                }
            }
        };

        this.init = function(){
            var cEvent = null;
            var a = this;

            element.addEventListener('touchstart', function(e){
                cEvent = new SwipeEvent(e.changedTouches[0]);
            }, false);

            element.addEventListener('touchmove', function(e){
            }, false);

            element.addEventListener('touchend', function(e){
                cEvent.onEnd(e.changedTouches[0]);
                handle(a, cEvent);
            }, false);

            return this;
        };
    };

    this.make = function(element, speed, ph, pw){
        speed = speed ? speed: 200;
        ph = ph ? ph: 2;
        pw = pw ? pw: 6;
        return new SwipePane(element, speed, ph, pw).init();
    };
};