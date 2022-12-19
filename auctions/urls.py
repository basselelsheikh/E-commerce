from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/",views.create_listing, name="create"),
    path("listings/<int:pk>",views.listing_detail,name="listing-detail"),
    path("listings/<int:pk>/close-auction/", views.close_auction_view,name="close-auction"),
    path("my-listings/",views.user_listings,name="user-listings"),
    path("my-bids/",views.user_bids,name="user-bids"),
    path("categories/",views.categories_view,name="categories"),
    path("categories/<int:pk>",views.category_detail,name="category-detail"),
    path("my-watchlist/",views.watchlist_view,name="user-watchlist"),
    path("listings/<int:pk>/add-to-watchlist/",views.add_to_watchlist,name="add-to-watchlist")

]
