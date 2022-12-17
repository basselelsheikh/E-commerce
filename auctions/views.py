from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Bid
from .forms import CreateListingForm, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(status='a')
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
    # if form is submitted
    if request.method == "POST":
        # if a comment was submitted
        if "text" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.commenter = request.user
                comment.listing = listing
                comment.save()
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
            "bid_form": bid_form
        }
        return render(request, "auctions/listing-detail.html", context)


     # if first time page is requested
    else:
        context = {'listing': listing}
        if request.user.is_authenticated:
            context["comment_form"] = CommentForm()
            if listing.lister != request.user:
                context["bid_form"] = BidForm()
        return render(request, "auctions/listing-detail.html", context)
