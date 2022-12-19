from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bid, Comment, Category, Watchlist
from .forms import CreateListingForm, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(status=Listing.Status.ACTIVE)
    context = {"listings": listings}
    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='/login')
def create_listing(request):
    # if form is submitted
    if request.method == "POST":
        form = CreateListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.lister = request.user
            listing.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            context = {"form": form}
            return render(request, 'auctions/create.html', context)
    # if first time page is requested
    else:
        context = {"form": CreateListingForm()}
        return render(request, 'auctions/create.html', context)


def listing_detail(request, pk):
    listing = Listing.objects.get(id=pk)
    comments = listing.comments.all()
    no_of_bids = len(listing.bids.all())
    is_bidder = False
    is_owner = True if listing.lister == request.user else False
    try:
        highest_bid = listing.bids.get(price=listing.current_price)
        is_bidder = True if highest_bid.bidder == request.user else False
    except:
        pass

    # if form is submitted
    if request.method == "POST":
        # if a comment was submitted
        if "text" in request.POST:
            comment = Comment(commenter=request.user, listing=listing)
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment = comment_form.save()
                comment.save()
                return HttpResponseRedirect(request.path_info)
            else:
                bid_form = BidForm()

        # if a bid was submitted
        if "price" in request.POST:
            bid = Bid(bidder=request.user, listing=listing)
            bid_form = BidForm(request.POST, instance=bid)
            if bid_form.is_valid():
                bid = bid_form.save()
                listing.current_price = bid.price
                listing.save()
                return HttpResponseRedirect(request.path_info)
            else:
                comment_form = CommentForm()
        context = {
            'listing': listing,
            "comment_form": comment_form,
            "bid_form": bid_form,
            "comments": comments,
            "is_bidder": is_bidder,
            "no_of_bids": no_of_bids,
            "is_owner": is_owner
        }
        return render(request, "auctions/listing_detail.html", context)

     # if first time page is requested
    else:
        context = {'listing': listing,
                   "comments": comments, "is_bidder": is_bidder, "no_of_bids": no_of_bids, "is_owner": is_owner}
        if request.user.is_authenticated:
            context["comment_form"] = CommentForm()
            if not is_owner:
                context["bid_form"] = BidForm()
        return render(request, "auctions/listing_detail.html", context)

@login_required
def close_auction_view(request, pk):
    listing = Listing.objects.get(id=pk)
    listing.status = Listing.Status.CLOSED
    # if there are bids, get the highest bidder and set him as the winner
    try:
        highest_bidder = listing.bids.get(price=listing.current_price)
        listing.winner = User.objects.get(id=highest_bidder.bidder.id)
    except:
        print("cant find winner")

    listing.save()
    return HttpResponseRedirect(listing.get_absolute_url())

@login_required
def user_listings(request):
    listings = Listing.objects.filter(lister=request.user)
    context = {"listings": listings}
    return render(request, "auctions/user_listings.html", context)

@login_required
def user_bids(request):
    bids = Bid.objects.filter(bidder=request.user)
    context = {"bids": bids}
    return render(request, "auctions/user_bids.html", context)


def categories(request):
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return render(request, "auctions/categories.html", context)

def category_detail(request,pk):
    category = Category.objects.get(id=pk)
    return render(request,"auctions/category_detail.html",context={"category":category, "listings": category.listings.filter(status=Listing.Status.ACTIVE)})

@login_required
def watchlist_view(request):
    try:
        listings = Watchlist.objects.get(prospect=request.user).listings
    except:
        listings=[]
    return render(request, "auctions/user_watchlist.html", context={"listings": listings})

@login_required
def add_to_watchlist(request,pk):
    watchlist = Watchlist(prospect=request.user)
    watchlist.listings.add(Listing.objects.get(pk=pk))
    watchlist.save()
    return HttpResponseRedirect(reverse(""))