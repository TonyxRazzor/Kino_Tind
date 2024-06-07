function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

$(document).ready(function() {
    checkForNotifications();

    $('.select-film').on('click', function() {
        var filmId = $(this).data('film-id');
        var selection = $(this).data('selection');
        var url = $(this).data('url');

        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'film_id': filmId,
                'selection': selection,
                'csrfmiddlewaretoken': getCsrfToken()
            },
            success: function(response) {
                if (response.success) {
                    if (selection === 'no') {
                        // Скрыть фильм из списка без перезагрузки страницы
                        $(`.film-card[data-film-id="${filmId}"]`).remove();
                    } else if (selection === 'yes') {
                        // Обновить кнопки на "Вы уже выбрали этот фильм"
                        let filmCard = $(`.film-card[data-film-id="${filmId}"]`);
                        filmCard.find('.button-container').html('<p>Вы уже выбрали этот фильм</p>');

                        if (response.matched) {
                            alert('Найдено совпадение для выбранного фильма!');
                        }
                    }
                } else {
                    alert('Совпадение не найдено. Пожалуйста, выберите другой фильм.');
                    location.reload();
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка:', error);
            }
        });
    });

    function checkForNotifications() {
        $.get(checkNotificationsUrl, function(data) {
            if (data.notifications.length > 0) {
                data.notifications.forEach(function(notification) {
                    alert(notification.title + ": " + notification.body);
                    if (notification.url) {
                        window.location.href = notification.url;
                    }
                });
            }
        });
    }

    setInterval(checkForNotifications, 5000);
});

function checkMatch() {
    fetch(checkUserMatchUrl)
        .then(response => response.json())
        .then(data => {
            if (data.matched) {
                alert(`Найдено совпадение для фильма ${data.title}`);
                window.location.href = `/users/confirm_match_result/${data.film_id}/`;
            }
        })
        .catch(error => console.error('Error:', error));
}

setInterval(checkMatch, 5000);

document.addEventListener('DOMContentLoaded', function() {
    const watchBtn = document.getElementById('watch-btn');
    const anotherBtn = document.getElementById('another-btn');

    if (watchBtn && anotherBtn) {
        watchBtn.addEventListener('click', function() {
            handleSelection(this);
        });

        anotherBtn.addEventListener('click', function() {
            handleSelection(this);
        });
    }

    function handleSelection(button) {
        const selection = button.getAttribute('data-selection');
        const filmId = button.getAttribute('data-film-id');
        const action = button.getAttribute('data-action');

        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: 'selection=' + selection + '&film_id=' + filmId + '&csrfmiddlewaretoken=' + getCsrfToken()
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.action === 'user_profile') {
                    window.location.href = userProfileUrl;
                } else if (data.action === 'film_selection') {
                    window.location.href = filmSelectionUrl;
                }
            } else {
                console.error('Error:', data.error_message);
                alert('Ошибка при обработке выбора');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при отправке запроса на сервер');
        });
    }
});
