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

////////////////////////////////////
//////////////Поиски////////////////
////////////////////////////////////

let main_search_form = document.forms.main_search_form;
let second_search_form = document.getElementById('search_form');
let second_search_form_was_populated = false

if (main_search_form) {
    let search_query_input = main_search_form.elements.search_query;
    search_query_input.addEventListener('focus', process_main_search_input);
    search_query_input.addEventListener('input', process_main_search_input);
    search_query_input.addEventListener('blur', function (event) {
        let search_panel = document.querySelector('.search-panel');
        if (search_panel) {
            let promise = new Promise(function(resolve, reject) {
                setTimeout(() => resolve(search_panel.remove()), 100);
            })
        }
    })
}
if (second_search_form) {
    let title_input = second_search_form.elements.title;
    title_input.addEventListener('focus', process_second_search_form_input);
    title_input.addEventListener('input', process_second_search_form_input);
    title_input.addEventListener('blur', function (event) {
        let search_panel = document.querySelector('.search-panel');
        if (search_panel) {
            let promise = new Promise(function(resolve, reject) {
                setTimeout(() => resolve(search_panel.remove()), 100);
            })
        }
    })

    second_search_form.elements.title.addEventListener('change', process_second_search_form_change);
    second_search_form.elements.from_price.addEventListener('change', process_second_search_form_change);
    second_search_form.elements.to_price.addEventListener('change', process_second_search_form_change);
    second_search_form.elements.size.addEventListener('change', process_second_search_form_change);
    second_search_form.elements.color.addEventListener('change', process_second_search_form_change);

    process_second_search_form_change();
}

async function process_main_search_input (event) {
    let fetch_url = window.location.origin + '/api/v1/search/'
    let search_query_input = event.target;

    if (search_query_input !== document.activeElement) return;

    let search_query = search_query_input.value;

    fetch_url += '?search_query=' + search_query;
    fetch_url += '&only_titles=' + 'True';

    let response = await fetch(fetch_url);
    let response_json = await response.json();

    let search_panel = document.querySelector('.search-panel');
    if (search_panel) search_panel.innerHTML = '';
    if (!search_panel) search_panel = create_search_panel_and_attache_to_input(search_query_input);

    for (let product_title of response_json.products_title) {
        create_search_panel_item_and_attache_to_panel(search_panel, product_title);
    }
}

async function process_second_search_form_input (event) {
    let fetch_url = window.location.origin + '/api/v1/search/'
    let title_input = event.target;

    if (title_input !== document.activeElement) return;

    let title = title_input.value;
    let category_title = title_input.dataset.category;
    let subcategory_title = title_input.dataset.subcategory;
    let search_query = title_input.dataset.search_query;
    let sort = second_search_form.elements.sort.value;
    let from_price = second_search_form.elements.from_price.value;
    let to_price = second_search_form.elements.to_price.value;
    let size = second_search_form.elements.size.value;
    let color = second_search_form.elements.color.value;

    if (!category_title) category_title = '';
    if (!subcategory_title) subcategory_title = '';
    if (!search_query) search_query = '';
    if (!from_price) from_price = '';
    if (!to_price) to_price = '';

    fetch_url += '?title=' + title;
    fetch_url += '&category=' + category_title;
    fetch_url += '&subcategory=' + subcategory_title;
    fetch_url += '&search_query=' + search_query;
    fetch_url += '&sort=' + sort;
    fetch_url += '&from_price=' + from_price;
    fetch_url += '&to_price=' + to_price;
    fetch_url += '&size=' + size;
    fetch_url += '&color=' + color;
    fetch_url += '&only_titles=' + 'True';

    let response = await fetch(fetch_url);
    let response_json = await response.json();

    let search_panel = document.querySelector('.search-panel');
    if (search_panel) search_panel.innerHTML = '';
    if (!search_panel) search_panel = create_search_panel_and_attache_to_input(title_input);

    for (let product_title of response_json.products_title) {
        create_search_panel_item_and_attache_to_panel(search_panel, product_title);
    }
}

async function process_second_search_form_change (event) {
    let form = second_search_form;
    let loader = document.getElementById('search-form-loader');
    loader.classList.add('show');
    const query_string = window.location.search;
    const url_params = new URLSearchParams(query_string);

    let fetch_url = window.location.origin + '/api/v1/search/'
    try {
        let title = form.elements.title.value;
        let category_title = form.elements.title.dataset.category;
        let subcategory_title = form.elements.title.dataset.subcategory;
        let search_query = form.elements.title.dataset.search_query;
        let sort = form.elements.sort.value;
        let from_price = form.elements.from_price.value;
        let to_price = form.elements.to_price.value;
        let size = form.elements.size.value;
        let color = form.elements.color.value;

        if (!second_search_form_was_populated && url_params.has('size')) {
            size = url_params.get('size');
        }
        if (!second_search_form_was_populated && url_params.has('color')) {
            color = url_params.get('color');
        }

        if (!category_title) category_title = '';
        if (!subcategory_title) subcategory_title = '';
        if (!search_query) search_query = '';
        if (!from_price) from_price = '';
        if (!to_price) to_price = '';

        fetch_url += '?title=' + title;
        fetch_url += '&category=' + category_title;
        fetch_url += '&subcategory=' + subcategory_title;
        fetch_url += '&search_query=' + search_query;
        fetch_url += '&sort=' + sort;
        fetch_url += '&from_price=' + from_price;
        fetch_url += '&to_price=' + to_price;
        fetch_url += '&size=' + size;
        fetch_url += '&color=' + color;

        let response = await fetch(fetch_url);
        let response_json = await response.json();

        document.getElementById('total-products-count-from-search').textContent = response_json.total_products_count;

        let size_select = form.elements.size;
        let current_size = size_select.value;
        let first_size_option = size_select.options[0];
        size_select.innerHTML = '';
        first_size_option.removeAttribute('selected');
        size_select.append(first_size_option);
        for (let size of response_json.sizes) {
            let new_option = new Option(size, size);
            size_select.append(new_option);
        }

        if (response_json.sizes.includes(current_size)) {
            size_select.value = current_size;
        } else {
            size_select.selectedIndex = 0;
        }
        if (!second_search_form_was_populated && url_params.has('size')) {
            size_select.value = url_params.get('size');
        }

        let color_select = form.elements.color;
        let current_color = color_select.value;
        let first_color_option = color_select.options[0];
        color_select.innerHTML = '';
        color_select.append(first_color_option);
        for (let color of response_json.colors) {
            let new_option = new Option(color, color);
            color_select.append(new_option);
        }

        if (response_json.colors.includes(current_color)) {
            color_select.value = current_color;
        } else {
            color_select.selectedIndex = 0;
        }
        if (!second_search_form_was_populated && url_params.has('color')) {
            color_select.value = url_params.get('color');
        }

        second_search_form_was_populated = true;
    } finally {
        loader.classList.remove('show');
    }
}

function create_search_panel_and_attache_to_input (attached_input) {
    let panel = document.createElement('div');
    panel.classList.add('search-panel');

    panel.addEventListener('click', function (event) {process_click_on_search_panel(event, attached_input)});

    panel.style.width = attached_input.offsetWidth + 'px';
    attached_input.closest('div').append(panel);
    return panel;
}

function process_click_on_search_panel (event, attached_input) {
    let panel_item = event.target.closest('.search-panel-item');
    attached_input.value = panel_item.textContent;

    let attached_input_form = attached_input.form;
    if (attached_input_form == main_search_form) {
        attached_input_form.submit();
    }
}

function create_search_panel_item_and_attache_to_panel (attached_panel, text_content) {
    let panel_item = document.createElement('div');
    panel_item.classList.add('search-panel-item');

    panel_item.textContent = text_content;

    attached_panel.append(panel_item);
    return panel_item;
}

////////////////////////////////////
///////////End Поиски///////////////
////////////////////////////////////

// В input c этим классом можно ввсести только цифры
let only_digits_in_input_inputs = document.querySelectorAll('.only-digits');
if (only_digits_in_input_inputs.length != 0) {
    for (let target_input of only_digits_in_input_inputs) {
        target_input.addEventListener('keydown', type_only_numbers);
    }
}

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

    let fetch_url = window.location.origin + '/api/v1/cart/';

    let response = await fetch(fetch_url);
    let cart_info = await response.json();

    cart_items_quantity.textContent = '(' + cart_info['cart_items_quantity'] + ')';
    cart_total_price.textContent = '(' + pretty_price(cart_info['cart_total_price'].toString()) +' грн.)';
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

function pretty_price (string_price) {

    new_prise = '';
    for (let i = string_price.length - 1; i >= 0; i--) {

        let index = string_price.length - 1 - i;
        if ((index) % 3 == 0) {
            new_prise += ' ' + string_price[i];
        } else {
            new_prise += string_price[i];
        }
    }

    new_prise = new_prise.split("").reverse().join("");
    return new_prise;
}
