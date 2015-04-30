var Account = new function(){
    this.signLabel = document.getElementById('sign-label');

    this.defaultOut = '<a class="button blue round" onclick="Account.signOut();">Sign out</a>';

    this.signOut = function(){
        Jax.get('sign_out', function(){
            Account.signLabel.innerHTML = '';
            Jax.refresh();
        });
    };

    this.signIn = function(form){
        var next = Jax.fn.focusNext();

        if(next.getAttribute('type') == 'submit'){
            var pass = form.confirm.type == 'hidden' || form.confirm.value != '';

            if((form.username.value != '' || form.password.value != '') && pass){
                if(form.confirm.type == 'hidden' || (form.password.value == form.confirm.value)){
                    form.ajax(function(data){
                        if(data.json().status == 'true'){
                            Account.signLabel.innerHTML = Account.defaultOut;
                            Jax.load('home');
                        }else{
                            Jax.fn.select("a[name=status]").text(data.json().message);
                        }
                    });
                }else{
                    Jax.fn.select("a[name=status]").text("passwords don't match");
                }
            }else{
                Jax.fn.select("a[name=status]").text('empty fields');
            }
        }
    };
};
