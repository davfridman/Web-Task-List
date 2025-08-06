document.addEventListener('DOMContentLoaded', () => {
    
    // --- Settings Menu Logic ---
    const settingsBtn = document.getElementById('settings-btn');
    const settingsMenu = document.getElementById('settings-menu');

    if (settingsBtn) {
        settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevents the window click listener from firing immediately
            settingsMenu.classList.toggle('active');
        });
    }

    // Hide settings menu if clicking outside
    window.addEventListener('click', () => {
        if (settingsMenu && settingsMenu.classList.contains('active')) {
            settingsMenu.classList.remove('active');
        }
    });

    // --- Modal Logic ---
    function openModal(modal) {
        if (modal == null) return;
        modal.classList.add('active');
        document.getElementById('overlay').classList.add('active');
        
        const itemNameInput = modal.querySelector('#item-name');
        if (itemNameInput) itemNameInput.focus();
        
        const categoryNameInput = modal.querySelector('input[name="category_name"]');
        if (categoryNameInput) categoryNameInput.focus();

        const listNameInput = modal.querySelector('input[name="list_name"]');
        if (listNameInput) listNameInput.focus();

        const editListNameInput = modal.querySelector('#edit-list-name');
        if (editListNameInput) editListNameInput.focus();
    }

    function closeModal(modal) {
        if (modal == null) return;
        modal.classList.remove('active');
        document.getElementById('overlay').classList.remove('active');
    }

    document.querySelectorAll('[data-modal-target]').forEach(button => {
        button.addEventListener('click', () => {
            const modal = document.querySelector(button.dataset.modalTarget);
            openModal(modal);
            // Hide settings menu when a modal is opened from it
            if (settingsMenu && settingsMenu.contains(button)) {
                settingsMenu.classList.remove('active');
            }
        });
    });

    document.querySelectorAll('[data-close-button]').forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    document.getElementById('overlay').addEventListener('click', () => {
        document.querySelectorAll('.modal.active').forEach(modal => closeModal(modal));
    });

    // --- Item Completion Logic ---
    document.addEventListener('change', e => {
        if (e.target.matches('.item-completed-checkbox')) {
            const checkbox = e.target;
            const itemId = checkbox.dataset.itemId;
            const isCompleted = checkbox.checked ? 1 : 0;
            fetch(`/toggle_completed/${itemId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_completed: isCompleted })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const itemElement = checkbox.closest('.sortable-item');
                    if (checkbox.checked) {
                        itemElement.classList.add('completed');
                    } else {
                        itemElement.classList.remove('completed');
                    }
                }
            });
        }
    });

    // --- SortableJS for Items ---
    document.querySelectorAll('.item-list').forEach(list => {
        new Sortable(list, {
            group: 'items',
            animation: 150,
            filter: '.item-completed-checkbox, .edit-item-btn, .add-sub-item-btn, a', // Ignore clicks on interactive elements
            onEnd: handleSortableEnd
        });
    });

    // --- SortableJS for Categories ---
    const listContainer = document.getElementById('list-container');
    if (listContainer) {
        new Sortable(listContainer, {
            animation: 150,
            handle: 'h3',
            onEnd: function(evt) {
                const categoryIds = [];
                listContainer.querySelectorAll('.category-group').forEach(group => {
                    categoryIds.push(group.dataset.categoryId);
                });
                fetch('/update_category_order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category_ids: categoryIds })
                });
            }
        });
    }

    function handleSortableEnd(evt) {
        const item = evt.item;
        const newCategoryId = evt.to.closest('.category-group').dataset.categoryId || null;
        
        const siblingIds = [];
        evt.to.querySelectorAll('.sortable-item').forEach(sibling => {
            siblingIds.push(sibling.dataset.itemId);
        });

        fetch('/update_item_and_order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: item.dataset.itemId,
                new_category_id: newCategoryId,
                sibling_ids: siblingIds
            })
        });
    }

    // --- Edit/Add Item Forms ---
    const itemModal = document.getElementById('modal-item');
    const itemForm = document.getElementById('item-form');
    const moreOptionsBtn = document.getElementById('more-options-btn');
    const moreOptionsContent = document.getElementById('more-options-content');

    if (moreOptionsBtn) {
        moreOptionsBtn.addEventListener('click', () => {
            moreOptionsContent.classList.toggle('active');
        });
    }
    
    document.addEventListener('click', e => {
        const addToCategoryBtn = e.target.closest('.add-item-to-category-btn');

        if (addToCategoryBtn) {
            const categoryId = addToCategoryBtn.dataset.categoryId;
            itemForm.reset();
            itemForm.action = '/add';
            document.getElementById('item-category_id').value = categoryId;
            itemModal.querySelector('.title').textContent = 'Add Item';
            moreOptionsContent.classList.remove('active');
            openModal(itemModal);
        }
    });

    document.querySelector('[data-modal-target="#modal-item"]').addEventListener('click', () => {
        itemForm.reset();
        itemForm.action = '/add';
        document.getElementById('item-id').value = '';
        itemModal.querySelector('.title').textContent = 'Add New Item';
        moreOptionsContent.classList.remove('active');
    });

    document.addEventListener('click', e => {
        const editBtn = e.target.closest('.edit-item-btn');
        if (editBtn) {
            const itemId = editBtn.dataset.itemId;
            fetch(`/item/${itemId}`).then(res => res.json()).then(data => {
                itemForm.reset();
                itemForm.action = `/update_item/${itemId}`;
                document.getElementById('item-id').value = data.id;
                document.getElementById('item-name').value = data.name;
                document.getElementById('item-quantity').value = data.quantity;
                document.getElementById('item-notes').value = data.notes;
                document.getElementById('item-who_needs_it').value = data.who_needs_it;
                document.getElementById('item-who_will_buy_it').value = data.who_will_buy_it;
                document.getElementById('item-category_id').value = data.category_id;
                document.getElementById('item-is_completed').checked = data.is_completed;
                itemModal.querySelector('.title').textContent = 'Edit Item';

                if (data.notes || data.who_needs_it || data.who_will_buy_it || data.quantity > 1) {
                    moreOptionsContent.classList.add('active');
                } else {
                    moreOptionsContent.classList.remove('active');
                }
                openModal(itemModal);
            });
        }
    });
    
    if (itemForm) {
        itemForm.addEventListener('submit', e => {
            const url = itemForm.action;
            if (url.includes('/update_item/')) {
                e.preventDefault();
                const formData = new FormData(itemForm);
                const data = Object.fromEntries(formData.entries());
                data.is_completed = itemForm.querySelector('#item-is_completed').checked ? 1 : 0;
                
                fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                }).then(() => location.reload());
            }
        });
    }

    // --- Inline Item Name Editing ---
    document.addEventListener('click', e => {
        if (e.target.matches('.item-name')) {
            const itemNameElement = e.target;
            const currentName = itemNameElement.textContent;
            const itemId = itemNameElement.dataset.itemId;

            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentName;
            
            itemNameElement.replaceWith(input);
            input.focus();

            function saveName() {
                const newName = input.value;
                if (newName && newName !== currentName) {
                    fetch(`/update_item_name/${itemId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: newName })
                    }).then(() => {
                        input.replaceWith(itemNameElement);
                        itemNameElement.textContent = newName;
                    });
                } else {
                    input.replaceWith(itemNameElement);
                }
            }

            input.addEventListener('blur', saveName);
            input.addEventListener('keydown', e => {
                if (e.key === 'Enter') {
                    saveName();
                } else if (e.key === 'Escape') {
                    input.replaceWith(itemNameElement);
                }
            });
        }
    });

    // --- Inline Category Name Editing ---
    document.addEventListener('click', e => {
        if (e.target.matches('.category-name')) {
            const categoryNameElement = e.target;
            const currentName = categoryNameElement.textContent.trim();
            const categoryId = categoryNameElement.dataset.categoryId;

            if (currentName === 'Other') return;

            const input = document.createElement('input');
            input.type = 'text';
            input.value = currentName;
            
            categoryNameElement.replaceWith(input);
            input.focus();

            function saveName() {
                const newName = input.value;
                if (newName && newName !== currentName) {
                    fetch(`/update_category/${categoryId}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: newName })
                    }).then(() => {
                        input.replaceWith(categoryNameElement);
                        categoryNameElement.textContent = newName;
                    });
                } else {
                    input.replaceWith(categoryNameElement);
                }
            }

            input.addEventListener('blur', saveName);
            input.addEventListener('keydown', e => {
                if (e.key === 'Enter') {
                    saveName();
                } else if (e.key === 'Escape') {
                    input.replaceWith(categoryNameElement);
                }
            });
        }
    });

    // --- Delete Category Logic ---
    document.addEventListener('click', e => {
        const deleteBtn = e.target.closest('.delete-category-btn');
        if (deleteBtn) {
            const categoryId = deleteBtn.dataset.categoryId;
            if (confirm('Are you sure you want to delete this category? All items will be moved to "Other".')) {
                fetch(`/delete_category/${categoryId}`, {
                    method: 'POST'
                }).then(() => location.reload());
            }
        }
    });
    
    // --- Edit List Name Logic ---
    const editListNameBtn = document.getElementById('edit-list-name-btn');
    const editListModal = document.getElementById('modal-edit-list');
    const editListForm = document.getElementById('edit-list-form');
    const deleteListBtn = document.getElementById('delete-list-btn');

    if (editListNameBtn) {
        editListNameBtn.addEventListener('click', () => {
            const listId = deleteListBtn.dataset.listId; // Assumes delete button has the active list ID
            fetch(`/list/${listId}`).then(res => res.json()).then(data => {
                document.getElementById('edit-list-id').value = data.id;
                document.getElementById('edit-list-name').value = data.name;
                openModal(editListModal);
            });
        });
    }

    if (editListForm) {
        editListForm.addEventListener('submit', e => {
            e.preventDefault();
            const listId = document.getElementById('edit-list-id').value;
            const newName = document.getElementById('edit-list-name').value;
            fetch(`/update_list/${listId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName })
            }).then(() => location.reload());
        });
    }

    // --- Delete List Logic ---
    if (deleteListBtn) {
        deleteListBtn.addEventListener('click', () => {
            const listId = deleteListBtn.dataset.listId;
            if (confirm('Are you sure you want to delete this list? This will also delete all its categories and items.')) {
                fetch(`/delete_list/${listId}`, {
                    method: 'POST'
                }).then(() => location.reload());
            }
        });
    }

    // --- Toggle Completed Items Logic ---
    const toggleCompletedBtn = document.getElementById('toggle-completed-btn');
    const toggleCompletedText = document.getElementById('toggle-completed-text');
    const toggleCompletedIcon = document.getElementById('toggle-completed-icon');

    const openEyeIcon = "/static/images/toggle_completed_icon.svg";
    const closedEyeIcon = "/static/images/toggle_completed_off_icon.svg";

    function setToggleState(hide) {
        if (hide) {
            listContainer.classList.add('hide-completed');
            toggleCompletedText.textContent = 'Show Completed';
            toggleCompletedIcon.src = closedEyeIcon;
            localStorage.setItem('hideCompleted', 'true');
        } else {
            listContainer.classList.remove('hide-completed');
            toggleCompletedText.textContent = 'Hide Completed';
            toggleCompletedIcon.src = openEyeIcon;
            localStorage.setItem('hideCompleted', 'false');
        }
    }

    // Check local storage on page load
    const shouldHideCompleted = localStorage.getItem('hideCompleted') === 'true';
    setToggleState(shouldHideCompleted);

    if (toggleCompletedBtn) {
        toggleCompletedBtn.addEventListener('click', () => {
            const isHidden = listContainer.classList.contains('hide-completed');
            setToggleState(!isHidden);
        });
    }
});
