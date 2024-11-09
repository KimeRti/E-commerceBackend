from src.utils.schemas import PaginationInfo

__all__ = ["get_pagination_info"]

def get_pagination_info(total_items: int, current_page: int, page_size: int):
    total_pages = (total_items + page_size - 1) // page_size
    has_previous = current_page > 1
    has_next = current_page < total_pages
    current_page_size = page_size if current_page != total_pages else total_items - (total_pages - 1) * page_size

    return PaginationInfo(
        currentPage=current_page,
        currentPageSize=current_page_size,
        hasNext=has_next,
        hasPrevious=has_previous,
        pageCount=total_pages,
        pageSize=page_size,
        remainingPages=max(0, total_pages - current_page),
        totalItems=total_items
    )
