def get_search_results_movies_message(movie_results: list, start_pos: int = 1):
    message = 'Выбери номер фильма для подробностей:\n\n'
    for i, result in enumerate(movie_results, start=start_pos):
        message += (
            f"{i}. {result['movie_name']}\n"
            f"💾 Размер: {result['size']}\n"
            f"🌟 Золотая раздача: {'✅' if result['is_gold'] else '❌'}\n"
            f"👥 Сиды: {result['sid']}\n\n"
        )
    return message


def get_search_result_movies_message(selected_movie: dict):
    message = (
        f"🎥 {selected_movie['movie_name']}\n"
        f"💾 Размер: {selected_movie['size']}\n"
        f"🌟 Gold: {'✅' if selected_movie['is_gold'] else '❌'}\n"
        f"👥 Сиды: {selected_movie['sid']}\n"
        f"🔗 Ссылка: {selected_movie['torrent_link']}\n"
    )
    return message
