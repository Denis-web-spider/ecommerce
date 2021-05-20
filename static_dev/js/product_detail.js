// Добавление товара в корзину
let product_form = document.getElementById('add_to_cart_form');
let quantity_input = product_form.elements.quantity;
let product_nav = document.querySelector('.product-nav');

product_form.addEventListener('submit', process_product_form);

quantity_input.addEventListener('keydown', type_only_numbers);
quantity_input.addEventListener('blur', process_quantity_input_blur);
product_nav.addEventListener('click', toggle_navigation_button);

async function process_product_form (event) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');

    if (quantity_input.value == '0') {
        let blur_event = new Event('blur', { bubbles: true, cancelable: true });
        quantity_input.dispatchEvent(blur_event);
    }

    let fetch_url = window.location.origin + '/api/v1/cart/';

    let form_data = new FormData(product_form);

    let response = await fetch(fetch_url, {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    });

    let result = await response.json();

    console.log(result);

    let my_message;
    if (result.detail && result.detail == 'Учетные данные не были предоставлены.') {
        let a = '<a href="' + login_url + '" class="alert-link">тут</a>'
        my_message = 'Только авторизованые пользователи могут добавлять товар в коризну. Авторизоваться можно ' + a + '.';
        alert_massage(my_message, 'danger');
    } else {
        let product_title = document.getElementById('product-title').textContent;
        let product_quantity = product_form.elements.quantity.value;
        my_message = product_title + ' X ' + product_quantity + ', добавлено в корзину';

        alert_massage(my_message, 'success');
        update_cart_info();
    }
}

function process_quantity_input_blur (event) {
    let target = event.target;

    if (target.value == '0' || target.value == '') {
        target.value = 1;
        target.setAttribute('value', 1);
    }
}
//////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////

// Комментарий

let add_review_form = document.getElementById('add-review-form');
if (add_review_form) {
    add_review_form.addEventListener('submit', process_add_review_form);
} else {
    console.log('User is not authenticated');
}

let current_user_review = document.getElementById('current-user-review');
if (current_user_review) {
    for (let button of current_user_review.querySelectorAll('button')) {
        button.addEventListener('click', populate_modal);
    }
}

let delete_review_modal = document.getElementById('delete-review-modal');
delete_review_modal.querySelector('form').addEventListener('submit', process_delete_review_form);

async function process_add_review_form (event) {
    event.preventDefault();
    form = event.target;
    const csrftoken = getCookie('csrftoken');

    if (!form.elements.ratting.value) {
        let my_message = 'Вы забыли поставить оценку нашему продукту. Это является обязательным, если Вы оставляете отзыв';
        alert_massage(my_message, 'danger');
        return;
    }

    if (form.dataset.modal) {
        let click_event = new Event('click', { bubbles: true, cancelable: true });
        form.closest('div[class~=modal]').querySelector('button.close').dispatchEvent(click_event);
    }

    let fetch_url = window.location.origin + '/api/v1/review/';

    let form_data = new FormData(form);

    let response = await fetch(fetch_url, {
        method: 'POST',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    })

    let result = await response.json();

    console.log(result);

    if (result.created == true) {
        create_current_user_review(form);

        let my_message = 'Ваш отзыв успешно добавлен';
        alert_massage(my_message, 'success');
        update_reviews_count('add');
    } else if (result.created == false) {
        update_current_user_review(form);

        let my_message = 'Ваш отзыв успешно отредактирован';
        alert_massage(my_message, 'success');
    }
}

async function process_delete_review_form (event) {
    event.preventDefault();
    form = event.target;
    const csrftoken = getCookie('csrftoken');

    let close_button = delete_review_modal.querySelector('button.close');
    let click_event = new Event('click', { bubbles: true, cancelable: true });
    close_button.dispatchEvent(click_event);

    current_user_review.remove();

    let fetch_url = window.location.origin + '/api/v1/review/';

    let form_data = new FormData(form);

    let response = await fetch(fetch_url, {
        method: 'DELETE',
        mode: 'same-origin',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: form_data
    })

    result = await response.json();

    console.log(result);

    if (result.deleted == true) {
        let my_message = 'Ваш отзыв был успешно удален';
        alert_massage(my_message, 'success');
        update_reviews_count('subtract');
    } else {
        let my_message = 'Ваш отзыв не был удален по какой-то причине';
        alert_massage(my_message, 'danger');
    }
}

function create_current_user_review (add_review_form) {
    let review_div = document.createElement('div');
    review_div.classList.add('reviews_submitted');
    review_div.setAttribute('id', 'current-user-review');
    review_div.style.backgroundColor = '#FFE0BC';
    review_div.style.padding = '5px';

    let buttons_div = document.createElement('div');
    buttons_div.style.display = 'inline';
    buttons_div.style.float = 'right';
    review_div.append(buttons_div);

    let edit_button = document.createElement('button');
    edit_button.classList.add('btn');
    edit_button.classList.add('btn-outline-danger');
    edit_button.setAttribute('type', 'button');
    edit_button.setAttribute('data-toggle', 'modal');
    edit_button.setAttribute('data-target', '#edit-review-modal');
    buttons_div.append(edit_button);

    let edit_button_icon = document.createElement('i');
    edit_button_icon.classList.add('fas');
    edit_button_icon.classList.add('fa-pen-square');
    edit_button_icon.classList.add('fa-lg');
    edit_button.append(edit_button_icon);

    let delete_button = document.createElement('button');
    delete_button.classList.add('btn');
    delete_button.classList.add('btn-outline-danger');
    delete_button.setAttribute('type', 'button');
    delete_button.setAttribute('data-toggle', 'modal');
    delete_button.setAttribute('data-target', '#delete-review-modal');
    buttons_div.append(delete_button);

    let delete_button_icon = document.createElement('i');
    delete_button_icon.classList.add('far');
    delete_button_icon.classList.add('fa-trash-alt');
    delete_button.append(delete_button_icon);

    let review_author_div = document.createElement('div');
    review_author_div.classList.add('reviewer');
    review_div.append(review_author_div);

    let review_author_first_name_span = document.createElement('span');
    review_author_first_name_span.classList.add('user-first-name');
    review_author_first_name_span.style.fontSize = '24px';
    review_author_first_name_span.style.fontWeight = 'bold';
    review_author_first_name_span.style.color = '#FF6F61';
    review_author_first_name_span.textContent = add_review_form.elements.first_name.value + ' ';
    review_author_div.append(review_author_first_name_span);

    let review_author_second_name_span = document.createElement('span');
    review_author_second_name_span.classList.add('user-second-name');
    review_author_second_name_span.style.fontSize = '24px';
    review_author_second_name_span.style.fontWeight = 'bold';
    review_author_second_name_span.style.color = '#FF6F61';
    review_author_second_name_span.textContent = add_review_form.elements.second_name.value;
    review_author_div.append(review_author_second_name_span);

    let ratting_div = document.createElement('div');
    ratting_div.classList.add('ratting');
    review_div.append(ratting_div);

    let ratting = +add_review_form.elements.ratting.value;
    for (let i = 0; i < 5; i++) {
        let star_icon = document.createElement('i');
        if (i + 1 <= ratting) {
            star_icon.classList.add('fa');
        } else {
            star_icon.classList.add('far');
        }
        star_icon.classList.add('fa-star');
        ratting_div.append(star_icon);
    }

    let user_review_text_p = document.createElement('p');
    user_review_text_p.classList.add('user-review');
    user_review_text_p.textContent = add_review_form.elements.review.value;
    review_div.append(user_review_text_p);

    let reviews_div = document.getElementById('reviews');
    reviews_div.prepend(review_div);

    for (let button of review_div.querySelectorAll('button')) {
        button.addEventListener('click', populate_modal);
    }
}

function populate_modal (event) {
    let target = event.target;
    if (target.tagName != 'BUTTON') target = target.closest('button');
    let modal = document.getElementById(target.dataset.target.replace('#', ''));

    current_user_review = document.getElementById('current-user-review');

    let first_name = current_user_review.querySelector('[class=user-first-name]').textContent;
    let second_name = current_user_review.querySelector('[class=user-second-name]').textContent;
    let review_text = current_user_review.querySelector('[class=user-review]').textContent;
    let ratting;
    let i = 0;
    for (let star_icon of current_user_review.querySelectorAll('.ratting i')) {
        i++;
        if (star_icon.classList.contains('fa')) ratting = i;
    }

    if (modal.dataset.action == 'edit') {
        modal.querySelector('[class="row form"]').replaceWith(add_review_form.querySelector('[class="row form"]').cloneNode(true));
        modal.querySelector('[class="row form"]').querySelector('div[class=row]').style.paddingLeft = '20px';

        let modal_form = modal.querySelector('form');
        modal_form.querySelector('[name=first_name]').value = first_name;
        modal_form.querySelector('[name=second_name]').value = second_name;
        modal_form.querySelector('[name=review]').value = review_text;

        for (let ratting_radio of modal_form.querySelectorAll('.stars input')) {
            if (ratting_radio.value == ratting) {
                let click_event = new Event('click', { bubbles: true, cancelable: true });
                ratting_radio.dispatchEvent(click_event);
            }
        }

        modal_form.addEventListener('submit', process_add_review_form);
    } else if (modal.dataset.action == 'delete') {
        modal.querySelector('.user-first-name').textContent = first_name;
        modal.querySelector('.user-second-name').textContent = second_name;
        modal.querySelector('.user-review').textContent = review_text;

        let i = 0;
        for (let star_icon of modal.querySelectorAll('.ratting i')) {
            i++;
            star_icon.classList.remove('fa');
            star_icon.classList.remove('far');
            if (i <= ratting) {
                star_icon.classList.add('fa');
            } else {
                star_icon.classList.add('far');
            }
        }
    }
}

function update_current_user_review (add_review_form) {
    let user_first_name = add_review_form.elements.first_name.value;
    let user_second_name = add_review_form.elements.second_name.value;
    let user_review_text = add_review_form.elements.review.value;
    let ratting = +add_review_form.elements.ratting.value;

    let current_user_review = document.getElementById('current-user-review');
    let span_first_name = current_user_review.querySelector('[class=user-first-name]');
    let span_second_name = current_user_review.querySelector('[class=user-second-name]');
    let p_review = current_user_review.querySelector('[class=user-review]');
    let div_ratting = current_user_review.querySelector('[class=ratting]');

    span_first_name.textContent = user_first_name;
    span_second_name.textContent = user_second_name;
    p_review.textContent = user_review_text;
    let i = 0;
    for (let star_icon of div_ratting.querySelectorAll('i')) {
        i++;

        star_icon.classList.remove('fa');
        star_icon.classList.remove('far');
        if (i <= ratting) {
            star_icon.classList.add('fa');
        } else {
            star_icon.classList.add('far');
        }
    }
}

function update_reviews_count (action) {
    let reviews_count_span = document.getElementById('reviews-count');
    let current_reviews_count = +reviews_count_span.textContent;
    if (action == 'add') {
        current_reviews_count += 1;
    } else if (action == 'subtract') {
        current_reviews_count -= 1;
    }
    reviews_count_span.textContent = current_reviews_count;
}

// End Комментарий

// Product nav

function toggle_navigation_button (event) {
    let navigation = this;
    let target_navigation_link = event.target.closest('.product-nav-link');

    let navigation_links = navigation.querySelectorAll('.product-nav-link');
    for (let navigation_link of navigation_links) {
        if (navigation_link != target_navigation_link) {
            navigation_link.classList.remove('active');
        }
    }
}

// End product nav
