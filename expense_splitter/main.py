from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required, logout_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.simple import BooleanField

from form import LoginForm, RegistrationForm, KittyForm, ExpenseAdditionForm
from models import User, db, ExpenseGroup, GroupMembers, Expense
from models import app
from collections import defaultdict


rando = 1001
@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_expense_groups = current_user.expense_groups
    return render_template('dashboard.html', is_user_logged_in=current_user.is_authenticated, user=current_user,
                           user_expense_groups=user_expense_groups)


# @app.route('/expenseform', methods=['GET', 'POST'])
# @login_required
# def expense_form():
#     form = KittyForm()
#     print(form.data)
#     print(request.form.getlist("participants"))
#     if form.validate_on_submit():
#         new_kitty = ExpenseGroup(
#             name=form.kitty_name.data,
#             creation_date=form.date.data,
#             creator_id=current_user.id
#         )
#
#         for participant_name in request.form.getlist("participants"):
#             if participant_name:
#                 new_kitty_participant = User.query.filter_by(name=participant_name).first()
#                 if new_kitty_participant:
#                     new_kitty.members.append(new_kitty_participant)
#
#                     group_member = GroupMembers(user_id=new_kitty_participant.id, group_id=new_kitty.id)
#                     db.session.add(group_member)
#
#         db.session.add(new_kitty)
#         db.session.commit()
#         return redirect(url_for('dashboard'))
#
#     return render_template('expense_form.html', form=form)


@app.route('/expenseform', methods=['GET', 'POST'])
@login_required
def expense_form():
    form = KittyForm()
    # print(form.data)
    # print(request.form.getlist("participants"))
    if form.validate_on_submit():
        new_kitty = ExpenseGroup(
            name=form.kitty_name.data,
            creation_date=form.date.data,
            creator_id=current_user.id
        )

        db.session.add(new_kitty)
        db.session.commit()  # Commit the new_kitty to get its ID

        for participant_name in request.form.getlist("participants"):
            if participant_name:
                # Create GroupMembers instance for each participant
                group_member = GroupMembers(member_name=participant_name, group_id=new_kitty.id)
                db.session.add(group_member)
        #creator_member = GroupMembers(id=rando,member_name=current_user.name, group_id=new_kitty.id)

        #db.session.add(creator_member)

        db.session.commit()  # Commit the changes to the GroupMembers table
        return redirect(url_for('dashboard'))

    return render_template('expense_form.html', form=form)


# @app.route('/addexpense', methods=['GET', 'POST'])
# def add_expense():
#     return render_template('add_expense.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        if len(form.password.data) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')
            return render_template('login.html', form=form, user=current_user)

    return render_template('login.html', form=form, user=current_user)


@app.route('/add_expense/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_expense(group_id):
    form = ExpenseAdditionForm()
    group = ExpenseGroup.query.get_or_404(group_id)
    group_members = GroupMembers.query.filter_by(group_id=group_id).all()
    creator_name = group.creator.name
    creator_member = GroupMembers(id=0,member_name=group.creator.name, group_id=group_id)

    #group_members.append(creator_member)
    #for member in group_members:
    #    db.session.add(member)
    #db.session.add(creator_member)
    # Populate the choices for group members in the form
    form.group_member_checkboxes.choices = [(str(member.id), member.member_name) for member in group_members]
    #form.group_member_checkboxes.choices.append((str(group.creator.id), creator_name))
# Populate the choices for the payer field
    form.payer.choices = [(str(member.id), member.member_name) for member in group_members]
    #form.payer.choices.append((str(group.creator.id), creator_name))
    if form.validate_on_submit():
        description = form.description.data
        amount = form.amount.data
        date = form.date.data
        split_equally = form.split_equally.data
        
        payer_id = form.payer.data
        print(form.payer.data)
        print(group.creator.id)
        ss = request.form.getlist('group_members[]')
        print(ss)

        if split_equally:
            total_members = len(group_members)
            amount_per_member = amount / total_members

            # Create an expense for each group member with split equally
            for member in group_members:
                expense = Expense(
                    description=description,
                    amount=amount_per_member,
                    date=date,
                    group_id=group_id,
                    payer_id=payer_id  # Associate the payer with the expense
                )
            for member in group_members:
                    #member = GroupMembers.query.get(member_id)
                    expense.members.append(member)
            db.session.add(expense)

            # Create an expense for the creator
            #creator_expense = Expense(
            #    description=description,
            #    amount=amount_per_member,
            #    date=date,
            #    group_id=group_id,
            #    payer_id=payer_id  # Associate the creator with the expense
            #)
           #db.session.add(creator_expense)
        else:
            selected_members = request.form.getlist('group_members[]')
            if selected_members:
                total_selected_members = len(selected_members)
                print(selected_members)
                amount_per_selected_member = amount / total_selected_members

                # Create an expense for each selected group member
                for member_id in selected_members:
                    expense = Expense(
                        description=description,
                        amount=amount_per_selected_member,
                        date=date,
                        group_id=group_id,
                        payer_id=payer_id  # Associate the selected payer with the expense
                    )
                for member_id in selected_members:
                    member = GroupMembers.query.get(member_id)
                    expense.members.append(member)

                db.session.add(expense)
            else:
                flash('Please select at least one group member for splitting differently.', 'warning')
                return redirect(url_for('add_expense', group_id=group_id))

        db.session.commit()
        return redirect(url_for('dashboard'))

    expenses = Expense.query.filter_by(group_id=group_id).all()
    return render_template('add_expense.html', form=form, group=group, expenses=expenses, group_members=group_members)



@app.route('/group_details/<int:group_id>')
@login_required
def group_details(group_id):
    group = ExpenseGroup.query.get_or_404(group_id)
    group_members = GroupMembers.query.filter_by(group_id=group_id).all()
    total_expense = db.session.query(db.func.sum(Expense.amount)).filter(Expense.group_id == group_id).scalar()
    total_members = len(group_members)+1
    expenses = Expense.query.filter_by(group_id=group_id).all()
    for expense in expenses:
        expense.group_members = GroupMembers.query.filter_by(group_id=group_id).all()

    creator_member = GroupMembers(id=0,member_name=group.creator.name, group_id=group_id)

    total_expenses = defaultdict(float)
    total_payments = defaultdict(float)
    for expense in expenses:
        total_expenses[expense.payer_id] += (expense.amount) * len(expense.members)
        for member in expense.members:
            total_payments[member.id] += expense.amount 

    # Calculate net balance for each member
    net_balance = defaultdict(float)
    for member_id in total_expenses.keys() | total_payments.keys():
        net_balance[member_id] = total_expenses[member_id] - total_payments[member_id]


    debts = {}

    for debtor, balance in net_balance.items():
        if balance < 0:
            debts[debtor] = {}
            for creditor, amount in net_balance.items():
                if amount > 0:
                    settle_amount = min(-balance, amount)
                    if settle_amount > 0:
                        debts[debtor][creditor] = settle_amount
                        balance += settle_amount
                        net_balance[creditor] -= settle_amount
                    if balance == 0:
                        break


    debts_with_names = {}
    for debtor_id, creditors in debts.items():
        debtor_name = next((member.member_name for member in group_members if member.id == debtor_id), None)
        if debtor_name:
            debts_with_names[debtor_name] = {}
            for creditor_id, amount in creditors.items():
                    creditor_name = next((member.member_name for member in group_members if member.id == creditor_id), None)
                    if creditor_name:
                        debts_with_names[debtor_name][creditor_name] = amount

    print(debts_with_names)          

    print(len(expenses))
    print(group_members[0].id)
    print(total_expenses)
    print(total_payments)
    print(debts)
    print(User.query.all()[0].id)


    return render_template('expense_details.html', total_members=total_members, group=group,
                           group_members=group_members, expenses=expenses, total_expense=total_expense, debts_with_names=debts_with_names)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)

#docker build -t expense-splitter .
#docker-compose up