let cart_table = document.querySelector('tbody[class~=cart-table]');
if (cart_table) {
    cart_table.addEventListener('input', recalculate_total_item_price);
    cart_table.addEventListener('change', set_zero_if_value_is_black)
    cart_table.addEventListener('keydown', type_only_numbers);
    cart_table.addEventListener('click', trigger_input_event_on_button_click);
} else {
    console.log('Корзина пуста');
}

function recalculate_total_item_price (event) {
    let target = event.target;
    if (target.value == '') return;
    if (target.value == '0' && event.isTrusted) {
        return;
    } else if (target.value == '0' && !event.isTrusted) {
        let delete_button = target.closest('tr').querySelector('button[data-action="delete"]');
        let click_event = new Event('click', { bubbles: true, cancelable: true });
        delete_button.dispatchEvent(click_event);
        return;
    }
    target.setAttribute('value', target.value);

    let item_id = target.dataset.item_id;
    let item_price = +target.dataset.item_price.replace(',', '.');
    let item_total_price_td = document.querySelector('td[class="item-total-price"][data-item_id="' + item_id + '"]');
    let item_total_price = (item_price * +target.value).toFixed(2).toString().replace('.', ',');

    document.querySelector('span[class="quantity"][data-item_id="' + item_id + '"]').textContent = target.value + ' ';
    item_total_price_td.textContent = item_total_price + 'грн.';

    recalculate_total_cart_price();

    let item = {
        'id': item_id,
        'quantity' : target.value,
    }

    update_item_data(item);
}

function recalculate_total_cart_price () {
    let cart_total_price = 0;

    for (let item_total_price_td of document.querySelectorAll('td[class=item-total-price]')) {
        cart_total_price += parseFloat(item_total_price_td.textContent.replace(',', '.'));
    }
    cart_total_price = cart_total_price.toFixed(2).toString().replace('.', ',');

    document.querySelector('span[class=cart-total-price]').textContent = cart_total_price + 'грн.';

    if (cart_total_price == '0,00') {
        empty_cart();
    }
}

function set_zero_if_value_is_black (event) {
    let target = event.target;
    if (target.tagName != 'INPUT') return;

    if (target.value == '' || target.value == '0') {
        let delete_button = target.closest('tr').querySelector('button[data-action="delete"]');
        let click_event = new Event('click', { bubbles: true, cancelable: true });
        delete_button.dispatchEvent(click_event);
    }
}

function trigger_input_event_on_button_click (event) {
    let target = event.target;
    if (target.tagName == 'I') target = target.closest('button');
    if (target.tagName == 'BUTTON' && target.dataset.action == 'delete' && target.dataset.item_id) delete_item(target);
    if (!target || target.dataset.action != 'trigger_input_event') return;

    let input_event = new Event('input', { bubbles: true, cancelable: true });
    target.parentNode.querySelector('input').dispatchEvent(input_event);
}

function empty_cart () {
    cart_page = document.querySelector('div[class=cart-page]');

    let div = document.createElement('div');
    div.classList.add('col-md-4');
    div.classList.add('offset-md-4');
    div.classList.add('text-center');
    div.style.marginTop = '100px';
    div.style.marginBottom = '300px';

    let h1 = document.createElement('h1');
    h1.style.color = 'red';
    h1.textContent = 'Ваша корзина пуста';
    div.append(h1);

    cart_page.replaceWith(div);
}

async function update_item_data (item_object) {
    const csrftoken = getCookie('csrftoken');

    let form = new FormData(document.createElement('form'));
    for (let key in item_object) {
        form.append(key, item_object[key]);
    }

    let response = await fetch('http://localhost:8000/api/v1/cart/', {
      method: 'PATCH',
      mode: 'same-origin',
      headers: {
        'X-CSRFToken': csrftoken,
      },
      body: form
    });

    let result = await response.json();
    console.log(result);

    update_cart_info();
}

async function delete_item (target) {
    const csrftoken = getCookie('csrftoken');
    let item_id = target.dataset.item_id;

    let product_title = document.querySelector('[class="product-title"][data-item_id ="' + item_id + '"]').textContent;
    target.closest('tr').remove();
    for (let item_data of document.querySelectorAll('div[class="cart-summary"] [data-item_id="' + item_id + '"]')) {
        item_data.remove();
    }

    let form = new FormData(document.createElement('form'));
    form.append('id', item_id)

    let response = await fetch('http://localhost:8000/api/v1/cart/', {
      method: 'DELETE',
      mode: 'same-origin',
      headers: {
        'X-CSRFToken': csrftoken,
      },
      body: form
    });

    let result = await response.json();
    console.log(result);
    if (result == 'Item with id ' + item_id + ' was deleted successfully') {
        alert_massage('Товар ' + product_title + ' успешно удален из вашей корзины', 'success');
    }

    recalculate_total_cart_price();

    update_cart_info();
}
