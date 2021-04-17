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

