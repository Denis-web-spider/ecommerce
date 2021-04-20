$(function() {

	$(document).on({
		mouseover: function(event) {
			$(this).find('.far').addClass('star-over');
			$(this).prevAll().find('.far').addClass('star-over');
		},
		mouseleave: function(event) {
			$(this).find('.far').removeClass('star-over');
			$(this).prevAll().find('.far').removeClass('star-over');
		}
	}, '.rate');


	$(document).on('click', '.rate', function() {
		if ( !$(this).find('.star').hasClass('rate-active') ) {
			$(this).siblings().find('.star').addClass('far').removeClass('fas rate-active');
			$(this).find('.star').addClass('rate-active fas').removeClass('far star-over');
			$(this).prevAll().find('.star').addClass('fas').removeClass('far star-over');
		} else {
			console.log('has');
		}
	});

});

// Автодополнение поисков
document.addEventListener('DOMContentLoaded', function (event) {
    let search_form = document.forms.main_search_form;
    let search_query = search_form.elements.search_query;
    let category_search_query = document.getElementById('id_title');

    let search_query_old_value;

    search_query.addEventListener('input', retrieve_search_data_and_create_search_panel);
    search_query.addEventListener('blur', function (event) {
        let search_panel = document.querySelector('div[class~=search_panel]');
        if (search_panel) {
            let promise = new Promise(function(resolve, reject) {
                setTimeout(() => resolve(search_panel.remove()), 100);
            })
        }
    })
    if (category_search_query) {
        category_search_query.addEventListener('input', retrieve_search_data_and_create_search_panel);
        category_search_query.addEventListener('blur', function (event) {
            let search_panel = document.querySelector('div[class~=search_panel]');
            if (search_panel) {
                let promise = new Promise(function(resolve, reject) {
                setTimeout(() => resolve(search_panel.remove()), 100);
            })
            }
        })
    }

    async function retrieve_search_data_and_create_search_panel(event) {
        remove_panel();
        search_form = search_query.form;
        search_query = event.target;
        search_category = search_query.dataset.category;
        search_subcategory = search_query.dataset.subcategory;

        search_query_old_value = search_query.value;
        if (!search_query.value) {
            let search_panel = document.querySelector('div[class=search_panel]');
            if (search_panel) {
                document.querySelector('div[class=search_panel]').remove();
            }
            return;
        }
        let response;
        if (search_category == 'all') {
            response = await fetch(`http://localhost:8000/api/v1/search/?search_query=${search_query.value}&subsearch_query=${search_query.dataset.subsearch}`);
        }else if (search_category && !search_subcategory) {
            response = await fetch(`http://localhost:8000/api/v1/search/?search_query=${search_query.value}&category=${search_category}`);
        } else if (search_subcategory) {
            response = await fetch(`http://localhost:8000/api/v1/search/?search_query=${search_query.value}&category=${search_category}&subcategory=${search_subcategory}`);
        } else {
            response = await fetch(`http://localhost:8000/api/v1/search/?search_query=${search_query.value}`);
        }
        let response_json = await response.json();

        let panel = document.querySelector('div[class~=search_panel]');
        if (!panel) {
            panel = document.createElement('div');
            panel.classList.add('search_panel');
            if (search_category) panel.classList.add('category_search_panel');
            resize_search_panel();
            panel.addEventListener('mouseover', fill_search_on_mouseover);
            panel.addEventListener('mouseout', clear_search_on_mouseout);
            panel.addEventListener('click', submit_search_form_on_click);
            search_query.closest('div').append(panel);

            window.addEventListener('resize', resize_search_panel);
        }

        for (let search_element of response_json) {
            let div = document.createElement('div');
            div.classList.add('search_panel_item');
            if (search_category) div.classList.add('category_search_panel_item');
            div.textContent = search_element;
            panel.append(div);
        }

        function remove_panel() {
            let current_panel = document.querySelector('div[class~=search_panel]');
            if (current_panel) {
                current_panel.remove();
            }
        }

        function fill_search_on_mouseover(event) {
            let target = event.target;
            if (!target.classList.contains('search_panel_item')) return;

            if (search_category) {
                search_query.value = target.textContent;
            } else {
                search_query.value = target.textContent;
                search_query.style.backgroundColor = '#FFC3BD';
            }
        }

        function clear_search_on_mouseout(event) {
            let target = event.target;
            if (!target.classList.contains('search_panel_item')) return;

            search_query.value = search_query_old_value;
            search_query.style.backgroundColor = '';
        }

        function submit_search_form_on_click(event) {
            let target = event.target;
            if (!target.classList.contains('search_panel_item')) return;

            search_query.value = target.textContent;
            search_query.style.backgroundColor = '';
            panel.remove();
            if (!search_category) search_form.submit();
        }

        function resize_search_panel(event) {
            panel.style.width = search_query.offsetWidth + 'px';
        }
    }
})


// Вспомогательные функции
let z_index = 100;
function alert_massage (message, status) {
    let container_fluid = document.createElement('div');
    container_fluid.classList.add('container-fluid');
    container_fluid.style.position = 'fixed';
    container_fluid.style.zIndex = z_index;
    container_fluid.style.marginTop = '50px';

    z_index += 1;

    let row = document.createElement('div');
    row.classList.add('row');
    container_fluid.append(row);

    let col = document.createElement('div');
    col.classList.add('col-md-8');
    col.classList.add('offset-md-2');
    col.classList.add('text-center');
    row.append(col);

    let alert = document.createElement('div');
    alert.classList.add('alert');
    alert.classList.add('alert-' + status);
    alert.classList.add('alert-dismissible');
    alert.classList.add('fade');
    alert.classList.add('show');
    alert.setAttribute('role', 'alert');
    col.append(alert);

    alert.innerHTML = message;

    let close_button = document.createElement('button');
    close_button.classList.add('close');
    close_button.setAttribute('type', 'button');
    close_button.setAttribute('data-dismiss', 'alert');
    close_button.setAttribute('aria-label', 'Close');
    alert.append(close_button);

    let span = document.createElement('span');
    span.setAttribute('aria-hidden', 'true');
    span.innerHTML = '&times;';
    close_button.append(span);

    document.body.prepend(container_fluid);

    new Promise(function (resolve, reject) {
        setTimeout(delete_alert, 3500);
    })

    function delete_alert () {
        let click_event = new Event('click', { bubbles: true, cancelable: true });
        close_button.dispatchEvent(click_event);
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function update_cart_info () {
    let cart_items_quantity = document.getElementById('cart-items-quantity');
    let cart_total_price = document.getElementById('cart-total-price');

    let response = await fetch('http://localhost:8000/api/v1/cart/');
    let cart_info = await response.json();

    cart_items_quantity.textContent = '(' + cart_info['cart_items_quantity'] + ')';
    cart_total_price.textContent = '(' + cart_info['cart_total_price'].toFixed(2).toString().replace('.', ',') +'грн.)';
}

function type_only_numbers (event) {
    if (event.key == 'Enter') event.target.blur();
    if (event.key == 'Backspace') return;
    if (!is_digit(event.key)) {
        event.preventDefault();
        return;
    }
}

function is_digit (string) {
    if (string >= '0' && string <= '9') {
        return string;
    } else {
        return false;
    }
}
