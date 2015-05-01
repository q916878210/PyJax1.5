var Jax = new function(){

    var state = new function(){
        this.ready = false;
    };

    var fn = new function(){

        this.focusNext = function(type, exAttr){
            if (!type) type = 'input';
            if (!exAttr) exAttr = ['type', 'hidden'];
            var t = document.activeElement;
            while(t = t.nextElementSibling){
                if(t == null){
                    break;
                }else if(t.tagName.toLowerCase() == type && t.getAttribute(exAttr[0]) != exAttr[1]){
                    t.focus();
                    break;
                }
            }
            return t != null? t: document.activeElement;
        };

        this.guid = function(){
            function s4(){
                return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
            }
            return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
        };

        this.preventDefault = function(e){
            e = e || window.event;
            if (e.preventDefault) e.preventDefault();
            e.returnValue = false;
        };

        this.string = new function(){
            var quotes = {'\'': '&#39;', '"': '&#34;'};

            this.replaceQuote = function (str) {
                for (var key in quotes) {
                    str = this.replaceAll(str, key, quotes[key]);
                }
                return str;
            };

            this.encode = function (str) {
                return encodeURI(str);
            };

            this.replaceAll = function (str, find, replace) {
                return str.replace(new RegExp(find, 'g'), replace);
            };

            this.contains = function(str, find){
                return str.indexOf(find) > -1;
            };
        };

        this.isNodeList = function(nodes){
            var stringRepr = Object.prototype.toString.call(nodes);

            return typeof nodes === 'object' &&
                /^\[object (HTMLCollection|NodeList|Object)\]$/.test(stringRepr) &&
                nodes.hasOwnProperty('length') &&
                (nodes.length === 0 || (typeof nodes[0] === "object" && nodes[0].nodeType > 0));
        };

        this.select = function(selector){
            var elements = null;
            if(selector != null) {
                if(typeof selector == 'string' || selector instanceof String) {
                    var sel = document.querySelectorAll(selector);
                    if (sel != null) {
                        elements = new obj.list(sel);
                    }
                }else if (typeof selector == 'element') {
                    elements = new obj.list([selector]);
                }else if (fn.string.contains(selector.constructor.toString(), 'ElementConstructor')) {
                    elements = new obj.list([selector]);
                }else if (fn.isNodeList(selector)){
                    elements = new obj.list(selector);
                }else{
                    elements = new obj.list([selector]);
                }
            }else{
                elements = new obj.list([]);
            }
            return elements;
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

    var obj = new function(){
        this.list = function(items){
            this.all = items;
            this.element = function(pos){
                if(pos == null) pos = 0;
                return this.all[pos];
            };

            this.forEach = function(func){
                for(var i=0; i<this.all.length; i++){
                    func(this.all[i]);
                }
            };

            this.click = function(func){
                this.forEach(function(element){
                    element.onclick = func;
                });
            };

            this.hasClass = function(name, func){
                this.forEach(function(element){
                    if(fn.cls.has(element, name)){
                        func(element);
                    }
                });
            };

            this.removeClass = function(name){
                this.forEach(function(element){
                    fn.cls.remove(element, name);
                });
            };

            this.addClass = function(name){
                this.forEach(function(element){
                    fn.cls.add(element, name);
                });
            };

            this.toggleClass = function(name){
                this.forEach(function(element){
                    fn.cls.toggle(element, name);
                });
            };

            this.html = function(data){
                var div = document.createElement('div');
                div.innerHTML = data;
                var scriptString = '';
                var scripts = div.getElementsByTagName('script');
                var oLen = scripts.length;
                for(var i=0; i<scripts.length; i++){
                    if(!scripts[i].hasAttribute('src')){
                        scriptString += scripts[i].innerHTML;
                        div.removeChild(scripts[i]);
                        i--;
                    }
                }
                this.forEach(function(element){
                    element.innerHTML = div.innerHTML;
                });

                if(oLen > 0){
                    var script = document.createElement('script');
                    script.innerHTML = scriptString;
                    this.all[0].appendChild(script);
                }
            };

            this.text = function(data){
                this.forEach(function(element){
                    element.innerText = data;
                });
            };
        };
    };

    var attr = new function(){
        this.events = new function(){
            this.functionMap = {};
            this.getFunctionsForName = function (name){
                if(this.functionMap[name] == null){
                    this.functionMap[name] = {};
                }
                return this.functionMap[name];
            };

            this.add = function (event) {
                this.getFunctionsForName(event.name)[event.key] = event.callback;
            };

            this.remove = function(name, key){
                delete this.getFunctionsForName(name)[key];
            };

            this.triggerOnce = function(name, item){
                if(this.functionMap[name] != null){
                    this.trigger(name, item);
                    delete this.functionMap[name];
                }
            };

            this.trigger = function (name, item) {
                if (this.functionMap[name] != null) {
                    if(item != null){
                        for (var key in this.functionMap[name]) {
                            if (this.functionMap[name].hasOwnProperty(key)) {
                                try{
                                    this.functionMap[name][key](item);
                                }catch(e){
                                    e.jax = name;
                                    e.key = key;
                                    console.log(e);
                                }
                            }
                        }
                    }else{
                        for (var key in this.functionMap[name]) {
                            if (this.functionMap[name].hasOwnProperty(key)) {
                                try{
                                    this.functionMap[name][key]();
                                }catch(e){
                                    e.jax = name;
                                    e.key = key;
                                    console.log(e);
                                }
                            }
                        }
                    }
                }
            };
        };
    };

    var action = new function(){
        this.submit = function(func){
            var attr = {};
            Jax.fn.select(this.getElementsByTagName('input')).forEach(function(input){
                attr[input.getAttribute('name')] = input.value;
            });
            ajax(this.getAttribute('method'), this.getAttribute('action'), attr, func);
        };

        this.preventForms = function(){
            Jax.fn.select('form[method]').forEach(function(form){
                if(!form.jaxed){
                    form.jaxed = true;
                    form.mysubmit = form.onsubmit;
                    form.ajax = action.submit;
                    form.onsubmit = function(e){
                        fn.preventDefault(e);
                        if(this.mysubmit) this.mysubmit();
                    };
                }
            });
        };

        this.triggerReady = function(){
            state.ready = true;
            attr.events.triggerOnce('ready');
            attr.events.trigger('postReady');
        };

    };

    var ready = function(func){
        if(state.ready){
            func();
        }else{
            attr.events.add({name:'ready', key:fn.guid(), callback:func});
        }
    };

    var ajax = function(method, url, data, func){
        state.ready = false;
        var xml = new XMLHttpRequest();
        var multipart = "";

        xml.open(method, url, true);

        for(var key in data){
            multipart += key + '=' + data[key] + '&';
        }
        multipart = multipart.substring(0, multipart.length - 1);

        xml.onreadystatechange = function(){
            if(xml.readyState == 4){
                func({text: xml.responseText, xml: xml.responseXML, json:function(){
                    if(!this.jsonObj){
                        try{
                            this.jsonObj = JSON.parse(this.text);
                        }catch(e){
                            this.jsonObj = false;
                        }
                    }
                    return this.jsonObj;
                }});
                action.triggerReady();
            }else{
                state.ready = true;
            }
        };

        xml.send(multipart);
    };

    var get = function(action, func){
        var a = '?';
        if(fn.string.contains(action, '?')){
            a = '&';
        }
        ajax("GET", action + a + 'ajax=true', {}, func);
    };

    var post = function(action, data, func){
        ajax("POST", action, data, func);
    };

    this.fn = fn;
    this.ready = ready;
    this.ajax = ajax;
    this.get = get;
    this.post = post;

    this.onLoad = function(func){
        attr.events.add({name:'onLoad', key:fn.guid(), callback:func});
    };

    var page = new function(){
        var activeElements = null;
        var activePath = null;
        var activeHashElements = null;

        var setLoad = function(){

            Jax.fn.select('*[load]').click(function(e){
                load(this.getAttribute('href'), this.getAttribute('load'));
                fn.preventDefault(e);
            });

            if('{%!forms%}' == 'prevent'){
                action.preventForms();
            }

            attr.events.trigger("onLoad", [activePath, activeElements.all[0]]);
        };

        var activeHash = function(page){
            if(activeHashElements != null){
                activeHashElements.removeClass('active');
            }
            activeHashElements = Jax.fn.select('a[href="#' + page + '"]');
            activeHashElements.addClass('active');
        };

        var loadHash = function(){
            Jax.ready(function(){
                var a = Jax.fn.select('a[href="' + location.hash + '"]');
                if(a.all.length > 0){
                    var loaded = false;
                    a.forEach(function(element){
                        var l = element.getAttribute('load');
                        if(l){
                            if(Jax.fn.select(l).all.length > 0){
                                main(location.hash.toString().substring(1), l);
                                loaded = true;
                            }
                        }
                    });
                    if(!loaded){
                        history.replaceState(null, null, location.pathname);
                    }
                }else{
                    history.replaceState(null, null, location.pathname);
                    history.back();
                }
            });
        };

        var activeLink = function(page){
            if(activeElements != null){
                activeElements.removeClass('active');
            }
            activeElements = Jax.fn.select('[page="' + page + '"]');
            activeElements.addClass('active');
        };

        var state = function(page){
            if (history.pushState){
                history.pushState(null, null, page);
            }
        };

        var main = function(page, selector){
            if(selector == null || selector == ''){
                selector = '#{%!!frame_id%}';
            }
            var isPage = selector == '#{%!!frame_id%}';
            if(isPage){
                activePath = page;
                activeLink(page);
            }else{
                activeHash(page);
            }

            Jax.get(page, function(data){
                Jax.fn.select(selector).html(data.text);
            });

            return isPage;
        };

        var load = function(page, selector){
            var innerPage = false;
            if(fn.string.contains(page, '#')){
                innerPage = true;
                page = fn.string.replaceAll(page, '#', '');
            }
            if(page != location.pathname.substring(1)){
                if(main(page, selector)) {
                    state(page);
                }else{
                    state('#' + page);
                }
            }
        };

        this.load = load;


        this.syncPath = function(path){
            if(activePath != path){
                activePath = path;
                activeLink(path);
                if (history.replaceState){
                    history.replaceState(null, null, path);
                }
            }
        };

        this.refresh = function(){
            var page = location.pathname.substring(1);
            main(page);
            state(page);
        };

        attr.events.add({name:'postReady', key:'load', callback:setLoad});

        attr.events.add({name:'fullLoad', key:fn.guid(), callback:function(){

            Jax.fn.select('*[page]').click(function(e){
                load(this.getAttribute('page'));
            });

            if(window.onpopstate != null){
                attr.events.add({name:'popstate', key:fn.guid(), callback:window.onpopstate});
            }

            window.onpopstate = function(e){
                attr.events.trigger("popstate", e);
                var path = location.pathname.substring(1);
                if(path != ''){
                    if (path != activePath){
                        main(path);
                    }else if(!location.hash){
                        main(path);
                    }
                    if(location.hash){
                        loadHash();
                    }
                }else{
                    activeLink(activePath);
                    if (history.replaceState){
                        history.replaceState(null, null, activePath);
                    }
                }
            };

            activePath = location.pathname.substring(1);
            if (activePath){
                activeLink(activePath);
                action.triggerReady();
                if(location.hash){
                    loadHash();
                }
            }
            else load('{%!home%}');
        }});
    };

    this.init = function(){
        if(window.onload != null){attr.events.add({name:'ready', key:fn.guid(), callback:window.onload});}

        window.addEventListener('load', function(){
            attr.events.triggerOnce('fullLoad');
        });
    };

    this.load = page.load;
    this.refresh = page.refresh;
    this.syncPath = page.syncPath;

    this.init();
};