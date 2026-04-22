
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

// Helper: strip _mobile suffix to get the canonical cart key (e.g. "pr5")
function getCanonicalId(rawId) {
    return rawId.replace('_mobile', '');
}

// Helper: get the numeric product id from a button id like "pr5" or "pr5_mobile"
function getCleanProductId(rawId) {
    return rawId.replace('_mobile', '').replace('pr', '');
}

$(document).on('click', '.cart', function () {
    var rawId = this.id.toString();
    var idstr = getCanonicalId(rawId);  // Always use canonical key in cart
    var cleanId = getCleanProductId(rawId);
    var isMobile = rawId.includes('_mobile');

    if (cart[idstr] != undefined) {
        qty = cart[idstr][0] + 1;
    }
    else {
        qty = 1;
        // Read name/price from the correct carousel (desktop or mobile)
        var suffix = isMobile ? '_mobile' : '';
        name = document.getElementById('name' + idstr + suffix).innerHTML;
        price = document.getElementById('price' + idstr + suffix).innerHTML;
        const selected = document.querySelector(`input[name="selected_size${cleanId}${suffix}"]:checked`);
        cart[idstr] = [qty, name, parseFloat(price), selected ? selected.value : ''];
    }
    updateCart(cart);
});

document.addEventListener("DOMContentLoaded", function () {
    for (let item in cart) {
        let itemId = item.replace("pr", "");
        radioValue = cart[item][3];
        // Sync both desktop and mobile radio buttons
        ['', '_mobile'].forEach(function(suffix) {
            let selected = document.querySelector(`input[name="selected_size${itemId}${suffix}"][value="${radioValue}"]`);
            if (selected) {
                selected.checked = true;
                selected.dispatchEvent(new Event("change"));
            }
        });
    }
    document.addEventListener("change", function (e) {
        if (e.target.name.startsWith("selected_size")) {
            let rawName = e.target.name.replace("selected_size", "");
            let itemId = rawName.replace("_mobile", "");
            let key = "pr" + itemId;
            if(cart[key]){
                cart[key][3] = e.target.value;
                // Sync the other carousel's radio button
                let otherSuffix = rawName.includes('_mobile') ? '' : '_mobile';
                let otherRadio = document.querySelector(`input[name="selected_size${itemId}${otherSuffix}"][value="${e.target.value}"]`);
                if (otherRadio && !otherRadio.checked) {
                    otherRadio.checked = true;
                }
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
        // Clear both desktop and mobile elements
        ['', '_mobile'].forEach(function(suffix) {
            var el = document.getElementById('div' + item + suffix);
            if (el) {
                var btnId = item + suffix;
                el.innerHTML = "<button id='" + btnId + "' class='btn btn-primary cart'>Add to cart</button>";
            }
        });
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
        // Update both desktop and mobile elements
        ['', '_mobile'].forEach(function(suffix) {
            var el = document.getElementById('div' + item + suffix);
            if (el) {
                var btnId = item + suffix;
                el.innerHTML = "<button id='minus" + btnId + "'class='btn btn-primary minus'>-</button> <span id='val" + btnId + "''" + ">" + cart[item][0] + "</span> <button id='plus" + btnId + "'class='btn btn-primary plus'> + </button>";
                if (cart[item][0] == 0) {
                    el.innerHTML = "<button id='" + btnId + "' class='btn btn-primary cart'>Add to cart</button>";
                }
            }
        });
        if (cart[item][0] == 0) {
            delete cart[item];
        }
    }
    localStorage.setItem(cartKey, btoa(JSON.stringify(cart)));
    if(document.getElementById('cart')){
        document.getElementById('cart').innerHTML = sum;
    }
    updatePopover(cart);
}

$('.divpr').on("click", "button.minus", function () {
    var rawId = this.id.slice(5,);  // Remove "minus" prefix -> e.g. "pr5" or "pr5_mobile"
    var canonicalId = getCanonicalId(rawId);
    var cleanNum = canonicalId.replace('pr', '');
    cart[canonicalId][0] = cart[canonicalId][0] - 1;
    cart[canonicalId][0] = Math.max(0, cart[canonicalId][0]);
    // Update both value displays
    ['', '_mobile'].forEach(function(suffix) {
        var valEl = document.getElementById('val' + canonicalId + suffix);
        if (valEl) valEl.innerHTML = cart[canonicalId][0];
    });
    updateCart(cart);
});

$('.divpr').on("click", "button.plus", function () {
    var rawId = this.id.slice(4,);  // Remove "plus" prefix -> e.g. "pr5" or "pr5_mobile"
    var canonicalId = getCanonicalId(rawId);
    var cleanNum = canonicalId.replace('pr', '');
    cart[canonicalId][0] = cart[canonicalId][0] + 1;
    // Update both value displays
    ['', '_mobile'].forEach(function(suffix) {
        var valEl = document.getElementById('val' + canonicalId + suffix);
        if (valEl) valEl.innerHTML = cart[canonicalId][0];
    });
    updateCart(cart);
});
