def generate_users(count=20):
    base_users = [
        {
            "id": 1,
            "name": "Johan Wiegand",
            "email": "johan@gmail.com",
            "phone": "+15550123456",
            "registered": "01 Jan, 2024",
            "last_login": "Today",
            "status": "Active",
            "role": "Admin"
        },
        {
            "id": 2,
            "name": "Kelsi Kuvalis",
            "email": "kelsi@yahoo.com",
            "phone": "+15559876543",
            "registered": "12 Feb, 2024",
            "last_login": "Yesterday",
            "status": "Inactive",
            "role": "Manager"
        },
        {
            "id": 3,
            "name": "Eulalia Crona",
            "email": "eulalia@hotmail.com",
            "phone": "+15558765432",
            "registered": "20 Mar, 2024",
            "last_login": "5 days ago",
            "status": "Active",
            "role": "Cashier"
        },
        {
            "id": 4,
            "name": "Aracely Sauer",
            "email": "aracely@gmail.com",
            "phone": "+15552345678",
            "registered": "15 Apr, 2024",
            "last_login": "2 days ago",
            "status": "Suspended",
            "role": "Superadmin"
        }
    ]

    users = []
    for i in range(count):
        template = base_users[i % len(base_users)].copy()
        template["id"] = i + 1
        users.append(template)

    return users


def generate_stats():
    return {
        "total_users": {"value": "12,000", "change": "+5% than last month"},
        "new_users": {"value": "350", "change": "+10% vs last month"},
        "pending_verifications": {"value": "42", "change": "2% of users"},
        "active_users": {"value": "7,800", "change": "65% of all users"},
    }



def generate_revenue_data():
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Soft drinks": [4800, 5300, 5100, 5050, 7800, 4600],
        "Frozen foods": [3500, 5600, 5300, 3800, 2800, 3000],
    }



def generate_visitors_data():
    return {
        "labels": ["Soft drinks", "Frozen foods", "Liquor"],
        "values": [65, 25, 10],
    }



def generate_activity(count=5):
    base = [
        {
            "user": "Johan Wiegand",
            "email": "johan@gmail.com",
            "status": "Active",
            "id": "#100001",
            "date": "5 min ago",
            "amount": "$250.00",
        },
        {
            "user": "Kelsi Kuvalis",
            "email": "kelsi@yahoo.com",
            "status": "Invited",
            "id": "#100002",
            "date": "12 min ago",
            "amount": "$480.00",
        },
        {
            "user": "Eulalia Crona",
            "email": "eulalia@hotmail.com",
            "status": "Suspended",
            "id": "#100003",
            "date": "20 min ago",
            "amount": "$320.00",
        },
        {
            "user": "Aracely Sauer",
            "email": "aracely@gmail.com",
            "status": "Inactive",
            "id": "#100004",
            "date": "35 min ago",
            "amount": "$150.00",
        },
        {
            "user": "Margot Oberbrunner",
            "email": "margot@yahoo.com",
            "status": "Active",
            "id": "#100005",
            "date": "45 min ago",
            "amount": "$900.00",
        },
    ]

    return [base[i % len(base)] for i in range(count)]
