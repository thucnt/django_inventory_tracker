from msilib.schema import ListView

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, UpdateView

from myrestaurant.forms import IngredientForm, MenuItemForm, RecipeRequirementForm
from myrestaurant.models import Ingredient, MenuItem, Purchase, RecipeRequirement


# Create your views here.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "myrestaurant/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ingredients"] = Ingredient.objects.all()
        context["menu_items"] = MenuItem.objects.all()
        context["purchases"] = Purchase.objects.all()

        return context

class IngredientsView(LoginRequiredMixin, ListView):
    template_name = "myrestaurant/ingredients_list.html"
    model = Ingredient

class NewIngredientView(LoginRequiredMixin, CreateView):
    template_name = "myrestaurant/add_ingredient.html"
    model = Ingredient
    form_class = IngredientForm

class UpdateIngredientView(LoginRequiredMixin, UpdateView):
    template_name = "myrestaurant/update_ingredient.html"
    model = Ingredient
    form_class = IngredientForm

class MenuView(LoginRequiredMixin, ListView):
    template_name = "myrestaurant/menu_list.html"
    model = MenuItem

class NewMenuItemView(LoginRequiredMixin, CreateView):
    template_name = "myrestaurant/add_menu_item.html"
    model = MenuItem
    form_class = MenuItemForm

class NewRecipeRequirementView(LoginRequiredMixin, CreateView):
    template_name = "myrestaurant/add_recipe_requirement.html"
    model = RecipeRequirement
    form_class = RecipeRequirementForm

class PurchaseView(LoginRequiredMixin, ListView):
    template_name = "myrestaurant/purchase_list.html"
    model = Purchase

class NewPurchaseView(LoginRequiredMixin, TemplateView):
    template_name = "myrestaurant/add_purchase.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["menu_items"] = [item for item in MenuItem.objects.all() if item.available()]

        return context

    def post(self, request):
        menu_item_id = request.POST["menu_item"]
        menu_item = MenuItem.objects.get(pk=menu_item_id)
        requirements = menu_item.reciperequirement_set
        purchase = Purchase(menu_item=menu_item)

        for requirement in requirements.all():
            requirement_ingredient = requirement.ingredient
            requirement_ingredient.quantity -= requirement.quantity
            requirement_ingredient.save()
        purchase.save()

        return redirect("/purchases")

class ReportView(LoginRequiredMixin, TemplateView):
    template_name = "myrestaurant/report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        revenue = Purchase.objects.aggregate(
            revenue=Sum("menu_item__price"))["revenue"]
        total_cost = 0
        for purchase in Purchase.objects.all():
            for recipe in purchase.menu_item.reciperequirement_set.all():
                total_cost += recipe.ingredient.price_per_unit * recipe.quantity

        context["purchases"] = Purchase.objects.all()
        context["revenue"] = revenue
        context["total_cost"] = total_cost
        context["profit"] = revenue - total_cost

        return context

def log_out(request):
    logout(request)
    return redirect("/")