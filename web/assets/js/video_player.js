var VideoPlayer = new function(){

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

    var uri = new function(){
        this.soundOnIcon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAwCAYAAAAPfWqeAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAAsTAAALEwEAmpwYAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgpMwidZAAAFb0lEQVRYCaWXS4hcVRCGeyaZGHyCj4gSZCAq+Awi6CKiQVSMICK4Udy5FBRXyUJcuRBchaCCEqLowpULRdQgZCEoGh8rIURjMOJbMRKjxMxM+33nnv/O6U63MJOC6qpTp96n7j23B4MVwHA4XKs69JqlpaVfoO+Ca6qs0BW4m6zaBLkW/mswsDsWCGbDr4rGAdQg34DCiY6U3x06hpsFZ043yBacHAYFgyyB/7oAFsF7arDS3hUHw0HOYLsegZPgAmggMZUdhL+kBlv5eWHctwJ+JygYaJGBGA/2Yiphv7eL7BSK0sihZg1dC74NDolh2xLIwILru2tV01uI0oxYFXu+rucq3YjOIVAowWplOa99yNPukYS1d2J6x/BnFGGVN3yeo/vRCeS8FrpOFvGD2sCdWlWE0FvAT8Ct48rI+r7D7wEFK3HqbFtbVTqwXBUKyfQm+COgcBDcVIP1U4QsulfB/woKTqKBpJ6f/LaRRBHkTG6G/xEU/urIcC80jvvMkOUMnq16BkhVGff2jdF1AqXbwB9AQUWNSnbQ7ROqSiCr+g0UUlXaZ2cu621ZnAV+CgrHQctu+/0z6yvbNrBuz+oV1oIBtDNJUXgogWZnZmaOs3gaofRMcNFNwKwXwA20/FEFgA4wcUC79iF7o+wMBrZ4CJpEfGyFH6CfdRnFHVoDPvE6bKv6nvUmjaA5s7RvAzIHR0hVad8XyM7WTsMYzMF/AAoxMKDPifBY1S9DwbodjleLxvLLNjZHkW/WztbpbA56kvVOhYDPwBLYtuEu9FCbsVLtClUZ2N+R0u60T3oeWM43WaWH77DxeTUykJCDvwF+XgEQWewPIDNRuxO70NLyKJJkydKB2Au2EJ1LEZbs2s3KH4Eerby+TMSKhI3+FCe0IeUq+9gfYNIUXd5t9U7qcuAb4vcs8BdWepE/yVY+cBjmGKh2ziltuDhKlSbrEzhPRWMq5ZwmBjJIjOIo1MMVsg71rfBPt9X/Zm+9rZxUkYOR4eitKlPeyONC1o7juE3654DMTgq0jo311VmU63Lw9xS5zqYlcdIkJgW6EKPzxxxG748qD0kiBuneANlZpk7yyBmlp1cjtypboSPlCfQdfAsJZJAk1+7Ll+SKAw8LyGTdWjXHA51AfrDuJUBdDvzMSqAkl72fZJJpAs4ju8MNIHs55EPIvio7yz/pwjyiTGSSCP1W9TiL8GFkvgF0nj3YAh9SdR5K33PapAubq46vIeUm4IDop0sOgzIt0CvAXOW5LfMWZmt4H0btNZEu+L39ngqAt7NJ5Hb21p7XrgcEb4KCV8T4fbQfWZkqqJm218v/XefvRz9ZPYftvaA3qo7SluKU9W7a5gfLWmjOLOdzJ/sXgNpOardJz1q2rcvEaBwHOaePkL0MCuVMNHRKq+0D3VaxS4L61H5f3VPetQGj3JKei70W7PXtVadc4S3P3rbuE07V/h9GbNt2z7a99osjwSxXeLI6tvKSVWiVv6USkHPVLoMQ2/5Tu50khXtA4TWdCfB97+Fti7JJ39/5KPF+8g3T+5YvwEZpDfQc8Amw3D2RqwSfiTsX/jNQaD9kEuilzmux6c4nguqoz3x8jcO+BfDPGAGwTXkU0rJjyG6s9v25tnEKj5IO10jbTdaTWqZzp89gqWZXDTKSdOtrKo+TtOw6+Hyjp2UGSpDR7+2pHids4KRkBr0e/BIU2iA+DpnSR3TBOg/6BI9TRDGCPgX630fHbcvy3LweF+yvqm15ftYtLi4+bzDACtoH+wDr/PWfPgDJZBrFSZ8h/AugkEr+hN+iLXT1QRK8dQK/CwyUdx2L0w8yJZiVPV4r6Z+x6J42xfkpE4Vs5JmbFOQ/oHzx4uzs6+oAAAAASUVORK5CYII=";
        this.soundButtonIcon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDUuNC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KTMInWQAAAkZJREFUeAHtWk1Kw0AUtmIEQejKhTcQXHgEwYWXEMFTiBtv4cJbiFdoQ+0fpbSbIDSrUrEuWpQUY9PqC60lTabJJMwzefENtEzm55vv+95bNJ23tcWNHWAH2AF2gB3IrAODwcDMLDlsYm/QvqFhn5M5fNBcGI/HlivebZkjiEmoUqnsTSaTr4X0xTfmeZnCLpVKh7Ztz7zi3X6mSGKRKZfLJ47jzP3i/4UB1Wr1fDYLBH7lBZbpmcCt1+tX87kw8Pk3oNVq3a5UhnQyESnVJLrd7n2I5rUp1WenjmcYxuOawoiH1AmrJGCa5lOE3sC0yvNTxer3+88BdRIDqZJWdfhwOHyV0CpcooqDCGdHNKh6DH7XfxSLxX3VuCrwEhtgWdanDAFN03bhU5BZm8aaxMTcXP0rwgVoWGdtYwFTwWUDqEQKiydnAJazVHA5A6hECosnZwCWs1RwOQOoRAqLJ2cAlrNUcDkDqEQKiydnAJazVHA5A6hECotn4gxw/6eTae12+xqLPBlcuAG+iLoBFl4ILAfJCA0jCqUvp2E1ALk3wDUHTDiaTqfhxQACJ8KMJTcHdUAHUAfkCHRuHCInMopws9nU4GbJ3qjYNxGFR3Z+NBq9+7QKH8kKlCEOt8YvQtWeQRkc0mugbsDw6A10SYuTJd/r9fSA8uWALAb5dVA79CAygbywOAI6nc6d34Q4+3OxFuoHb7wm5EJUXBGNRuPy9/0h7t7crK/Vamfu+0NuBCURouv6cZJ9vIcdYAfYAXaAHYh24Ac2iLWCoXcpmwAAAABJRU5ErkJggg==";
        this.soundOffIcon = "data:image/png;base64,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";
        this.playOnIcon = "data:image/png;base64,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";
        this.playOffIcon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAACXBIWXMAAAsTAAALEwEAmpwYAAABy2lUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS40LjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgICAgICAgICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIj4KICAgICAgICAgPHRpZmY6T3JpZW50YXRpb24+MTwvdGlmZjpPcmllbnRhdGlvbj4KICAgICAgICAgPHhtcDpDcmVhdG9yVG9vbD5BZG9iZSBJbWFnZVJlYWR5PC94bXA6Q3JlYXRvclRvb2w+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgqyI37xAAACOUlEQVR4Ae1aS07DQAxN+AhYoS64BGfhFCw5DgfgFKwqzsElWLHhIz7huYqrtHU6bjNYRjxLllOP59nzxukmbhoKGSADZIAMkAEyQAbIwP9koJ167K7rjpwYXdu2X55YYB4izlUbMD89mClicLDioTwxNQ9TLMhKJkVCYLoTrF9Dz6ByuxbeN/yn0Efsude9+L0hugZ7hcVL6Bv0YCOwaTr4pEteoXfAfde9Rmx9lyQTVNgZ1Cvzfo8UbgqAFmuwcy8o4mYCBmuRb+YZOr3v73DP8Flu4gl6Af2AWkXIOyod8Az1isZKB1g1St5jqOSW573FAt8VTDHEWgQo3ujNa8DAaqxgKv5geXloa20YV3y23q/iJisALbhwi1W14vbxKd4wxz441p5qBOCPyML/FV/NXNUI+JWTBoCSgACSU6dgB6S+noDi2AEBJKdOwQ5IfT0BxbEDAkhOnYIdkPp6AopjBwSQnDoFOyD19QQUxw4IIDl1CnZA6usJKI4dEEBy6hTsgNTXE1AcOyCA5NQp2AGpryeguGodoJ+uA2pefH6vlWfygIEWop+s1aq/hl3HXP89JUcNAnRMTaw1JCB+yeMakesPo7GK3buXRkdkxtaXgaWHqQTIgWU+SERmdizRHOfW4ohPY2W2aJtIbov0bXtW1rS4FecOP14QewN1jcn1uDI2Nya6douAB6hnTE5q+BuCP8ribXliap62WFApGQr2dhFHZUtkcp0MkAEyQAbIABkgA2QgkIEfb4rjI3P8Hy8AAAAASUVORK5CYII=";
        this.fullIcon = "data:image/png;base64,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";
    };

    var one = function(node, type, func){
        var a = function(){
            func();
            node.removeEventListener(type, a, false);
        };
        node.addEventListener(type, a, false);
    };

    var getControlHtml = function(){
        var html = '';

        html += '<ol class="video-button-bar-wrap">';

        html += '<li class="play">';
        html += '<img class="play-on" src="' + uri.playOnIcon + '" />';
        html += '<img class="play-off hide" src="' + uri.playOffIcon + '"/>';
        html += '</li>';

        html += '<li class="sound-button">';
        html += '<img class="sound-icon" src="' + uri.soundButtonIcon + '"/>';
        html += '<div class="vol-wrap">';
        html += '<img class="vol-on" src="' + uri.soundOnIcon + '"/>';
        html += '<img class="vol-off hide" src="' + uri.soundOffIcon + '"/>';
        html += '</div>';
        html += '</li>';

        html += '<li class="sound-slider">';
        html += '<div class="video-sound-slider-wrap">';

        html += '<a class="sound-slider-back"></a>';
        html += '<a class="sound-slider-fill"></a>';
        html += '<input class="video-slider" type="range" value="100">';

        html += '</div>';
        html += '</li>';

        html += '<li class="video-timer">';
        html += '<a>0:00</a>';
        html += '<a>/</a>';
        html += '<a>0:00</a>';
        html += '</li>';

        html += '<li class="full-screen">';
        html += '<img class="full-screen-icon" src="' + uri.fullIcon + '"/>';
        html += '</li>';
        html += '</ol>';

        html +=  '<div class="video-progress-wrap">';
        html += '<div class="video-progress-load"></div>';
        html += '<div class="video-progress-trail"></div>';
        html += '<input class="video-slider" type="range" min="0" max="1000" value="0">';
        html += '</div>';

        return html;
    };

    var getContextMenuHtml = function(){
        var html = '<ol>';
        html += '<li>Open Video</li>';
        html += '<li>Play/Pause</li>';
        html += '<li>Refresh</li>';
        return html + '</ol>';
    };

    var events = new function () {
        this.functionMap = {};

        this.getFunctionsForName = function (name) {
            if (this.functionMap[name] == null) {
                this.functionMap[name] = {};
            }
            return this.functionMap[name];
        };

        this.add = function(event){
            this.getFunctionsForName(event.name)[event.key] = event.callback;
        };

        this.remove = function(name, key){
            delete this.getFunctionsForName(name)[key];
        };

        this.trigger = function (name, item) {
            if (this.functionMap[name] != null) {
                if(item != null){
                    for (var key in this.functionMap[name]) {
                        if (this.functionMap[name].hasOwnProperty(key)) {
                            this.functionMap[name][key](item);
                        }
                    }
                }else{
                    for (var key in this.functionMap[name]) {
                        if (this.functionMap[name].hasOwnProperty(key)) {
                            this.functionMap[name][key]();
                        }
                    }
                }
            }
        };
    };

    function VideoObject(element){
        var isSeekAdjust = false;

        this.video = element;
        this.wrapper = document.createElement('DIV');
        this.wrapper.className = 'video-player';
        this.controls = document.createElement('DIV');
        this.controls.className = 'video-controls';
        this.contextMenu = document.createElement('DIV');
        this.contextMenu.className = 'video-menu hide';
        this.contextMenu.innerHTML = getContextMenuHtml();

        var progressWrap = null;
        var progressSlider = null;
        var trail = null;
        var loaded = null;
        var bar = null;

        var play = null;
        var playOn = null;
        var playOff = null;

        var soundButton = null;
        var volOn = null;
        var volOff = null;

        var soundSlider = null;
        var soundSliderFill = null;
        var fullScreen = null;

        var timerClock = null;
        var durationClock = null;

        var wrapper = this.wrapper;
        var video = this.video;
        var contextMenu = this.contextMenu;

        var openContextMenu = function(e){
            var x = 0; var y = 0;
            if(e.pageX) x = e.pageX;
            else if( e.clientX) x = e.clientX;
            if(e.pageY) y = e.pageY;
            else if( e.clientY) y = e.clientY;

            var bounds = wrapper.getBoundingClientRect();
            x -= bounds.left;
            y -= bounds.top;

            contextMenu.style.left = x + "px";
            contextMenu.style.top = y + 'px';
            cls.remove(contextMenu, 'hide');
        };

        var closeContextMenu = function(){
            cls.add(contextMenu, 'hide');
        };

        var getProgressOffsetWidth = function(){
            var offsetWidth = {offset: '', width: '', left: ''};
            var pBound = progressWrap.getBoundingClientRect();
            offsetWidth['left'] = parseFloat(pBound.left);
            offsetWidth['width'] = parseFloat(pBound.width);
            offsetWidth['offset'] = parseFloat(((16) * 100 / offsetWidth['width']).toFixed(2));
            return offsetWidth;
        };

        var setProgress = function(percent){
            video.currentTime = (video.duration * (percent / 100));
        };

        this.setProgress = setProgress;

        var onPause = function(){
            cls.add(playOff, 'hide');
            cls.remove(playOn, 'hide');
            isSeekAdjust = false;
        };

        var onPlay = function(){
            cls.add(playOn, 'hide');
            cls.remove(playOff, 'hide');
            isSeekAdjust = false;
        };

        this.onEnded = function(){
            cls.add(playOff, 'hide');
            cls.remove(playOn, 'hide');
            isSeekAdjust = false;
        };

        var updateProgress = function(){
            timerClock.innerText = video.currentTime.toFixed().toHHMMSS();
            if(!isSeekAdjust){
                var p = ((100 / video.duration) * video.currentTime);
                trail.style.width = p + '%';
                progressSlider.value = parseInt(p * 10);
            }
        };

        var updateLoaded = function(){
            var start = 0;
            var end = 0;
            var update = true;
            try{
                start = video.buffered.start(0);
                end = video.buffered.end(0);
            }catch(error){
                update = false;
            }
            if(update){
                loaded.style.left = start + '%';
                loaded.style.width = (((end / video.duration) * 100) - start) + '%';
            }
        };

        this.proTriggers = function(){
            progressSlider.onchange = function(){
                isSeekAdjust = false;
                setProgress(this.value / 10);
            };

            progressSlider.oninput = function(){
                isSeekAdjust = true;
                trail.style.width = (this.value / 10) + '%';
            };

            progressSlider.onfocus = function(){
                isSeekAdjust = true;
            };
        };

        this.barTriggers = function(){
            play.onclick = function(){
                if(cls.toggle(playOn, 'hide')){
                    cls.remove(playOff, 'hide');
                    video.play();
                }else{
                    cls.add(playOff, 'hide');
                    video.pause();
                }
            };

            soundButton.onclick = function(){
                if(cls.toggle(volOn, 'hide')){
                    cls.remove(volOff, 'hide');
                    video.muted = true;
                }else{
                    cls.add(volOff, 'hide');
                    video.muted = false;
                }
            };

            soundSlider.onchange = function(){
                soundSliderFill.style.width = this.value + '%';
                video.volume = this.value / 100;
            };

            soundSlider.oninput = function(){
                soundSliderFill.style.width = this.value + '%';
                video.volume = this.value / 100;
            };

            fullScreen.onclick = function(){
                if(video.mozRequestFullScreen){
                    video.mozRequestFullScreen();
                }else if(video.webkitRequestFullScreen){
                    video.webkitRequestFullScreen();
                }
            };
        };

        var setDuration = function(){
            durationClock.innerText = video.duration.toFixed().toHHMMSS();
        };

        var waitForDuration = function(){
            setTimeout(function(){
                if(isNaN(video.duration)){
                    waitForDuration();
                }else{
                    setDuration();
                    cls.add(wrapper, 'ready');
                }
            }, 1000);
        };

        this.init = function() {
            this.video.parentNode.appendChild(this.wrapper);
            this.video.parentNode.removeChild(this.video);

            var videoCont = document.createElement('DIV');
            videoCont.className = 'video-container';
            this.wrapper.appendChild(videoCont);
            this.wrapper.appendChild(this.contextMenu);
            videoCont.appendChild(this.video);
            videoCont.appendChild(this.controls);

            this.controls.innerHTML = getControlHtml();

            this.video.removeAttribute('controls');
            this.video.volume = 1;

            progressWrap = this.controls.getElementsByClassName('video-progress-wrap')[0];
            progressSlider = progressWrap.getElementsByTagName('input')[0];
            trail = progressWrap.getElementsByClassName('video-progress-trail')[0];
            loaded = progressWrap.getElementsByClassName('video-progress-load')[0];

            bar = this.controls.getElementsByClassName('video-button-bar-wrap')[0];

            play = bar.getElementsByClassName('play')[0];
            playOn = play.getElementsByClassName('play-on')[0];
            playOff = play.getElementsByClassName('play-off')[0];

            soundButton = bar.getElementsByClassName('sound-button')[0];
            volOn = soundButton.getElementsByClassName('vol-on')[0];
            volOff = soundButton.getElementsByClassName('vol-off')[0];

            var soundSliderP = bar.getElementsByClassName('sound-slider')[0];
            soundSlider = soundSliderP.getElementsByTagName('input')[0];
            soundSliderFill = soundSliderP.getElementsByClassName('sound-slider-fill')[0];

            fullScreen = bar.getElementsByClassName('full-screen')[0];

            var timerWrap = bar.getElementsByClassName('video-timer')[0];
            timerClock = timerWrap.children[0];
            durationClock = timerWrap.children[2];

            this.proTriggers();
            this.barTriggers();

            var menuChildren = contextMenu.getElementsByTagName('li');

            menuChildren[0].onclick = function(){
                window.open(video.src, '_blank');
            };
            menuChildren[1].onclick = function(){
                play.click();
            };
            menuChildren[2].onclick = function(){
                video.pause();
                onPause();
                var t = video.src;
                var p = video.currentTime;
                video.src = '';
                video.src = t;
                video.currentTime = p;
            };

            waitForDuration();

            this.video.addEventListener('timeupdate', updateProgress, false);
            this.video.addEventListener('progress', updateLoaded, false);
            this.video.addEventListener('ended', this.onEnded, false);
            this.video.addEventListener('play', onPlay, false);
            this.video.addEventListener('pause', onPause, false);

            this.wrapper.addEventListener('contextmenu', function(e){
                openContextMenu(e);
                one(document, 'click', closeContextMenu);
                e.preventDefault();
            }, false);

            return this;
        };
    }

    this.make = function(element){
        return new VideoObject(element).init();
    };

    (function(){
        if(window.onmousemove != null){
            events.add({name:'onmousemove', key:'default', callback:window.onmousemove});
        }
        if(window.onmouseup != null){
            events.add({name:'onmouseup', key:'default', callback:window.onmouseup});
        }

        window.onmousemove = function(e){
            events.trigger('onmousemove', e);
        };

        window.onmouseup = function(e){
            events.trigger('onmouseup', e);
        };

        String.prototype.toHHMMSS = function () {
            var sec_num = parseInt(this, 10);
            var hours   = Math.floor(sec_num / 3600);
            var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
            var seconds = sec_num - (hours * 3600) - (minutes * 60);

            if (seconds < 10) {seconds = "0"+seconds;}
            var time = '';
            if(hours != "00"){
                if (minutes < 10) {minutes = "0"+minutes;}
                time = hours + ':';
            }
            time += minutes + ':' + seconds;
            return time;
        };
    })();
};