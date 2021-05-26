let return_product_table = document.getElementById('return-product-table');
let add_return_product_item_button = document.querySelector('button[data-action=add-return-product-item]');

add_return_product_item_button.addEventListener('click', add_return_product_item);

function add_return_product_item (event) {
    let all_rows = return_product_table.querySelector('tbody').querySelectorAll('tr');
    let last_row = all_rows[all_rows.length - 1];
    let new_row = last_row.cloneNode(true);

    new_row.dataset.count = +new_row.dataset.count + 1;
    let old_product_formset_id = (new_row.dataset.count - 2).toString();
    let new_product_formset_id = (new_row.dataset.count - 1).toString();
    new_row.querySelector('th').textContent = new_row.dataset.count;
    for (let td of new_row.querySelectorAll('td')) {
        let input_or_select = td.querySelector('*');
        input_or_select.name = input_or_select.name.replace(old_product_formset_id, new_product_formset_id);
        input_or_select.id = input_or_select.id.replace(old_product_formset_id, new_product_formset_id);
        if (input_or_select.tagName == 'INPUT') {
            input_or_select.value = '';
        }

    document.getElementById('id_form-TOTAL_FORMS').value = new_row.dataset.count;
    }

    return_product_table.querySelector('tbody').append(new_row);
}
