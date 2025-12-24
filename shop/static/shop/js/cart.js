
var currentUser = window.currentUser || "guest";;
if (!currentUser) {
    currentUser = "guest";
}
var cartKey = "cart_" + currentUser;
var dummyKey = cartKey + "Dummy"
if (localStorage.getItem(cartKey) == null) {
    var cart = {};
}
else {
    cart = JSON.parse(atob(localStorage.getItem(cartKey)));
    document.addEventListener("DOMContentLoaded", function () {
        updateCart(cart);
    });
}

$(document).on('click', '.cart', function () {
    var idstr = this.id.toString();
    if (cart[idstr] != undefined) {
        qty = cart[idstr][0] + 1;
    }
    else {
        qty = 1;
        name = document.getElementById('name' + idstr).innerHTML;
        price = document.getElementById('price' + idstr).innerHTML;
        let cleanId = idstr.replace("pr", "");
        const selected = document.querySelector(`input[name="selected_size${cleanId}"]:checked`);
        cart[idstr] = [qty, name, parseFloat(price), selected.value];
    }
    updateCart(cart);
});
document.addEventListener("DOMContentLoaded", function () {
    for (let item in cart) {
        let itemId = item.replace("pr", "");
        radioValue = cart[item][3]
        let selected = document.querySelector(`input[name="selected_size${itemId}"][value="${radioValue}"]`);
        if (selected) {
            selected.checked = true;
            selected.dispatchEvent(new Event("change"));
        }
        
    }
    document.addEventListener("change", function (e) {
        if (e.target.name.startsWith("selected_size")) {
            let itemId = e.target.name.replace("selected_size", "");
            let key = "pr" + itemId;
            if(cart[key]){
                cart[key][3] = e.target.value;
            }
            localStorage.setItem(cartKey, btoa(JSON.stringify(cart)));
            updateCart(cart);
        }
    });
});


$(document).ready(function () {
    updatePopover(cart);
});
function updatePopover(cart) {
    var popStr = "";
    let length = Object.keys(cart).length;
    if (length > 0) {
        popStr = popStr + "<h5>Your Items In Cart</h5><div class='mx-2 my-2'>";
        var i = 1;
        for (var item in cart) {
            var name = cart[item][1];
            var qty = cart[item][0];
            popStr = popStr + "<b>" + i + "</b>. ";
            popStr = popStr + name.slice(0, 19) + "... Qty: (" + qty + ") " + '<br>';
            i = i + 1
        }
        popStr = popStr + `</div>
    <div class="d-flex gap-2 mt-2">
        <a href='/shop/checkout/?dummy=false' class='btn btn-success btn-sm' id="cartCheckOut">Check Out</a>
        <a href='#' id='clearCartLink' class='btn btn-danger btn-sm'>Clear Cart</a>
    </div>`;
    }
    else {
        popStr = popStr + "<h5>Your Cart is Empty...</h5><div class='mx-2 my-2'></div>";
    }
    $(document).ready(function () {
        var wasVisible = $('#popcart').next('.popover').is(':visible') || $('#popcart').attr('aria-describedby') !== undefined;
        $('#popcart').popover('dispose');
        $('#popcart').popover({
            content: popStr,
            html: true,
            trigger: 'click'
        });
        if (wasVisible) {
            $('#popcart').popover('show');
        }
    });

}

function clearCart() {
    cart = JSON.parse(atob(localStorage.getItem(cartKey)));
    for (var item in cart) {
        if (document.getElementById('div' + item)) {
            document.getElementById('div' + item).innerHTML = "<button id='" + item + "' class='btn btn-primary cart'>Add to cart</button>";
        }
    }
    localStorage.removeItem(cartKey);
    cart = {};
    updateCart(cart);
}
$(document).on('click', '#clearCartLink', function (e) {
    e.preventDefault();
    clearCart();
});
function updateCart(cart, hw = null) {
    var sum = 0;
    for (var item in cart) {
        sum = sum + cart[item][0];
        if (document.getElementById('div' + item)) {
            document.getElementById('div' + item).innerHTML = "<button id='minus" + item + "'class='btn btn-primary minus'>-</button> <span id='val" + item + "''>" + cart[item][0] + "</span> <button id='plus" + item + "'class='btn btn-primary plus'> + </button>";
            if (cart[item][0] == 0) {
                document.getElementById('div' + item).innerHTML = "<button id='" + item + "' class='btn btn-primary cart'>Add to cart</button>";
                delete cart[item];
            }
        }
        else {
            continue;
        }
    }
    localStorage.setItem(cartKey, btoa(JSON.stringify(cart)));
    document.getElementById('cart').innerHTML = sum;
    updatePopover(cart);
}

$('.divpr').on("click", "button.minus", function () {
    a = this.id.slice(7,);
    cart['pr' + a][0] = cart['pr' + a][0] - 1;
    cart['pr' + a][0] = Math.max(0, cart['pr' + a][0]);
    document.getElementById('valpr' + a).innerHTML = cart['pr' + a][0];
    updateCart(cart);
});

$('.divpr').on("click", "button.plus", function () {
    a = this.id.slice(6,);
    cart['pr' + a][0] = cart['pr' + a][0] + 1;
    document.getElementById('valpr' + a).innerHTML = cart['pr' + a][0];
    updateCart(cart);
});

