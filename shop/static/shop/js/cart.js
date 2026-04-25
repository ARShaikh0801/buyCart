
var currentUser = window.currentUser || "guest";
if (!currentUser) {
    currentUser = "guest";
}
var isAuthenticated = window.isAuthenticated || false;
var cartKey = "cart_" + currentUser;
var dummyKey = cartKey + "Dummy";

// The in-memory cart object
var cart = {};

// ── CSRF helper ────────────────────────────────────────────────
function getCSRFToken() {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var c = cookies[i].trim();
        if (c.startsWith('csrftoken=')) {
            return c.substring('csrftoken='.length);
        }
    }
    // Fallback: try to get from hidden input
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
}

// ── API helpers (authenticated users) ──────────────────────────
function apiRequest(url, method, body) {
    var opts = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    };
    if (body) {
        opts.body = JSON.stringify(body);
    }
    return fetch(url, opts).then(function (res) {
        if (res.status === 401) {
            console.warn("Cart API: Access denied (401). Falling back to localStorage.");
            isAuthenticated = false; // Toggle localized auth flag
            return { cart: lsGetCart(), totalItems: 0, _fallback: true };
        }
        if (!res.ok) throw new Error("API error: " + res.status);
        return res.json();
    }).catch(function(err) {
        console.error("Cart API Request failed:", err);
        return { cart: lsGetCart(), totalItems: 0, _error: true };
    });
}

function apiGetCart() {
    return apiRequest('/shop/api/cart/', 'GET', null);
}

function apiUpdateItem(productId, quantity, selectedSize) {
    return apiRequest('/shop/api/cart/update/', 'POST', {
        product_id: productId,
        quantity: quantity,
        selected_size: selectedSize,
    });
}

function apiRemoveItem(productId) {
    return apiRequest('/shop/api/cart/remove/', 'POST', {
        product_id: productId,
    });
}

function apiClearCart() {
    return apiRequest('/shop/api/cart/clear/', 'POST', {});
}

// ── localStorage helpers (guest users) ─────────────────────────
function lsGetCart() {
    var raw = localStorage.getItem(cartKey);
    if (raw) {
        try { return JSON.parse(atob(raw)); } catch (e) { return {}; }
    }
    return {};
}

function lsSaveCart(c) {
    localStorage.setItem(cartKey, btoa(JSON.stringify(c)));
}

// ── Helper: strip _mobile suffix to get the canonical cart key ──
function getCanonicalId(rawId) {
    return rawId.replace('_mobile', '');
}

// ── Helper: get numeric product id from button id like "pr5" ───
function getCleanProductId(rawId) {
    return rawId.replace('_mobile', '').replace('pr', '');
}

// ── Merge guest localStorage cart into DB cart on login ─────────
function mergeGuestCartIntoDB() {
    var guestKey = "cart_guest";
    var raw = localStorage.getItem(guestKey);
    if (!raw) return Promise.resolve();
    var guestCart;
    try { guestCart = JSON.parse(atob(raw)); } catch (e) { return Promise.resolve(); }
    if (!guestCart || Object.keys(guestCart).length === 0) return Promise.resolve();

    // Send each guest item to the API, merging quantities
    var promises = [];
    for (var itemKey in guestCart) {
        var productId = parseInt(itemKey.replace('pr', ''));
        var guestQty = guestCart[itemKey][0];
        var guestSize = guestCart[itemKey][3] || '';

        // If already in DB cart, add quantities
        (function(pid, gQty, gSize) {
            var existingQty = (cart['pr' + pid] && cart['pr' + pid][0]) || 0;
            promises.push(apiUpdateItem(pid, existingQty + gQty, gSize));
        })(productId, guestQty, guestSize);
    }

    return Promise.all(promises).then(function () {
        localStorage.removeItem(guestKey);
    });
}

// ── Initialise cart on page load ───────────────────────────────
function initCart() {
    if (isAuthenticated) {
        apiGetCart().then(function (data) {
            cart = data.cart || {};
            // Now attempt to merge any guest cart
            mergeGuestCartIntoDB().then(function () {
                // Re-fetch after merge
                return apiGetCart();
            }).then(function (data2) {
                cart = data2.cart || {};
                updateCart(cart);
                syncRadioButtons();
            });
        });
    } else {
        cart = lsGetCart();
        updateCart(cart);
        syncRadioButtons();
    }
}

// ── Render cart UI (badges, buttons, popover) ──────────────────
function renderCart(c) {
    var sum = 0;
    for (var item in c) {
        sum += c[item][0];
        // Update both desktop and mobile elements
        ['', '_mobile'].forEach(function(suffix) {
            var el = document.getElementById('div' + item + suffix);
            if (el) {
                var btnId = item + suffix;
                var btnId = item + suffix;
                el.innerHTML = "<button id='minus" + btnId + "' class='btn btn-primary minus'>-</button> <span id='val" + btnId + "' class='mx-3'>" + c[item][0] + "</span> <button id='plus" + btnId + "' class='btn btn-primary plus'> + </button>";
                if (c[item][0] == 0) {
                    el.innerHTML = "<button id='" + btnId + "' class='btn btn-primary cart'>Add to cart</button>";
                }
            }
        });
        if (c[item][0] == 0) {
            delete c[item];
        }
    }
    if (document.getElementById('cart')) {
        document.getElementById('cart').innerHTML = sum;
    }
    updatePopover(c);
}

// ── Save cart (route to the right backend) ─────────────────────
function saveCart(c) {
    if (!isAuthenticated) {
        lsSaveCart(c);
    }
    // For authenticated users the individual API calls already persist data
}

// ── updateCart: master function called after every mutation ─────
function updateCart(cart, hw) {
    renderCart(cart);
    saveCart(cart);
}

// ── Add to cart button click ───────────────────────────────────
$(document).on('click', '.cart', function () {
    var rawId = this.id.toString();
    var idstr = getCanonicalId(rawId);
    var cleanId = getCleanProductId(rawId);
    var isMobile = rawId.includes('_mobile');

    if (isAuthenticated) {
        // Authenticated: use API
        var productId = parseInt(cleanId);
        var newQty = 1;
        var suffix = isMobile ? '_mobile' : '';
        var selectedEl = document.querySelector('input[name="selected_size' + cleanId + suffix + '"]:checked');
        var selectedSize = selectedEl ? selectedEl.value : '';

        if (cart[idstr] != undefined) {
            newQty = cart[idstr][0] + 1;
            cart[idstr][0] = newQty;
        } else {
            var name = document.getElementById('name' + idstr + suffix).innerHTML;
            var price = document.getElementById('price' + idstr + suffix).innerHTML;
            cart[idstr] = [newQty, name, parseFloat(price), selectedSize];
        }

        // Optimistically update the UI to instantly show correct sizes
        updateCart(cart);

        apiUpdateItem(productId, newQty, selectedSize).then(function (data) {
            cart = data.cart || {};
            updateCart(cart);
        });
    } else {
        // Guest: localStorage
        if (cart[idstr] != undefined) {
            qty = cart[idstr][0] + 1;
        } else {
            qty = 1;
            var suffix = isMobile ? '_mobile' : '';
            name = document.getElementById('name' + idstr + suffix).innerHTML;
            price = document.getElementById('price' + idstr + suffix).innerHTML;
            var selected = document.querySelector('input[name="selected_size' + cleanId + suffix + '"]:checked');
            cart[idstr] = [qty, name, parseFloat(price), selected ? selected.value : ''];
        }
        updateCart(cart);
    }
});

// ── Sync radio buttons with cart state ──────────────────────────
function syncRadioButtons() {
    for (var item in cart) {
        var itemId = item.replace("pr", "");
        var radioValue = cart[item][3];
        ['', '_mobile'].forEach(function(suffix) {
            var selected = document.querySelector('input[name="selected_size' + itemId + suffix + '"][value="' + radioValue + '"]');
            if (selected) {
                selected.checked = true;
                selected.dispatchEvent(new Event("change"));
            }
        });
    }
}

// ── Radio button change listener ───────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener("change", function (e) {
        if (e.target.name.startsWith("selected_size")) {
            var rawName = e.target.name.replace("selected_size", "");
            var itemId = rawName.replace("_mobile", "");
            var key = "pr" + itemId;
            if (cart[key]) {
                cart[key][3] = e.target.value;
                // Sync the other carousel's radio button
                var otherSuffix = rawName.includes('_mobile') ? '' : '_mobile';
                var otherRadio = document.querySelector('input[name="selected_size' + itemId + otherSuffix + '"][value="' + e.target.value + '"]');
                if (otherRadio && !otherRadio.checked) {
                    otherRadio.checked = true;
                }

                if (isAuthenticated) {
                    apiUpdateItem(parseInt(itemId), cart[key][0], e.target.value).then(function (data) {
                        cart = data.cart || {};
                    });
                } else {
                    lsSaveCart(cart);
                }
                updateCart(cart);
            }
        }
    });
});

// ── Popover ────────────────────────────────────────────────────
$(document).ready(function () {
    updatePopover(cart);
});

function updatePopover(cart) {
    var popStr = "";
    var length = Object.keys(cart).length;
    if (length > 0) {
        popStr = popStr + "<h5>Your Items In Cart</h5><div class='mx-2 my-2'>";
        var i = 1;
        for (var item in cart) {
            var name = cart[item][1];
            var qty = cart[item][0];
            popStr = popStr + "<b>" + i + "</b>. ";
            popStr = popStr + name.slice(0, 19) + "... Qty: (" + qty + ") " + '<br>';
            i = i + 1;
        }
        popStr = popStr + `</div>
    <div class="d-flex gap-2 mt-2">
        <a href='/shop/checkout/?dummy=false' class='btn btn-success btn-sm' id="cartCheckOut">Check Out</a>
        <a href='#' id='clearCartLink' class='btn btn-danger btn-sm'>Clear Cart</a>
    </div>`;
    } else {
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

// ── Clear cart ─────────────────────────────────────────────────
function clearCart() {
    if (isAuthenticated) {
        apiClearCart().then(function (data) {
            // Reset UI buttons
            for (var item in cart) {
                ['', '_mobile'].forEach(function(suffix) {
                    var el = document.getElementById('div' + item + suffix);
                    if (el) {
                        var btnId = item + suffix;
                        el.innerHTML = "<button id='" + btnId + "' class='btn btn-primary cart'>Add to cart</button>";
                    }
                });
            }
            cart = {};
            renderCart(cart);
        });
    } else {
        cart = lsGetCart();
        for (var item in cart) {
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
        renderCart(cart);
    }
}

$(document).on('click', '#clearCartLink', function (e) {
    e.preventDefault();
    clearCart();
});

// ── Minus / Plus buttons ───────────────────────────────────────
$('.divpr').on("click", "button.minus", function () {
    var rawId = this.id.slice(5,);
    var canonicalId = getCanonicalId(rawId);
    var cleanNum = canonicalId.replace('pr', '');
    cart[canonicalId][0] = cart[canonicalId][0] - 1;
    cart[canonicalId][0] = Math.max(0, cart[canonicalId][0]);

    var newQty = cart[canonicalId][0];
    var size = cart[canonicalId][3] || '';

    // Optimistically update UI so 0-qty items reset to 'Add to Cart' before API deletes them
    updateCart(cart);

    if (isAuthenticated) {
        apiUpdateItem(parseInt(cleanNum), newQty, size).then(function (data) {
            cart = data.cart || {};
            updateCart(cart);
        });
    }
});

$('.divpr').on("click", "button.plus", function () {
    var rawId = this.id.slice(4,);
    var canonicalId = getCanonicalId(rawId);
    var cleanNum = canonicalId.replace('pr', '');
    cart[canonicalId][0] = cart[canonicalId][0] + 1;

    var newQty = cart[canonicalId][0];
    var size = cart[canonicalId][3] || '';

    updateCart(cart);

    if (isAuthenticated) {
        apiUpdateItem(parseInt(cleanNum), newQty, size).then(function (data) {
            cart = data.cart || {};
            updateCart(cart);
        });
    }
});

// ── Initialise on DOM ready ────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
    initCart();
});
