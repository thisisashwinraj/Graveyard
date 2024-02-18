import time
import uuid
from PIL import Image
from datetime import date, datetime
import streamlit as st
import streamlit_antd_components as sac

from database.db_utils import BookingsUtils, HallsUtils, CustomQuery
from database.firebase import fetch_user_full_name_by_username


st.set_page_config(
    page_title="SeminarSpace Admin Console",
    page_icon="assets/favicon/seminarspace_favicon.png",
    initial_sidebar_state="expanded",
    layout="wide",
)

st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 4.75rem;
                    padding-bottom: 0rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)


if __name__ == "__main__":
    if "admin_authentication_status" not in st.session_state:
        st.session_state.admin_authentication_status = None

    if st.session_state.admin_authentication_status is not True:
        st.markdown(
            "<H2 style='color: #ffffff;' align='center'>Welcome to the SeminarSpace Admin Console</H2><BR>",
            unsafe_allow_html=True,
        )

        _, form_col, _ = st.columns([1, 3.5, 1])

        with form_col:
            with st.form("admin_console_login_form"):
                input_admin_username = st.text_input(
                    "Username / Email Id:",
                    placeholder="Enter your Username/Email",
                    help="Access restricted to admins",
                )

                input_admin_password = st.text_input(
                    "Enter your Password:",
                    type="password",
                    placeholder="Enter your Admin Password",
                )

                _, login_button_col, _ = st.columns(3)

                with login_button_col:
                    admin_login_button = st.form_submit_button(
                        "LogIn as Admin", use_container_width=True
                    )

                if admin_login_button:
                    if (
                        input_admin_username == "myadmin"
                        or input_admin_username == "myadmin@gmail.com"
                    ) and input_admin_password == "adminpassword":
                        st.success(
                            "SignIn Approved! Welcome to SeminarSpace Admin Console"
                        )
                        st.session_state.admin_authentication_status = True
                        st.rerun()

                    else:
                        authentication_failed_alert = st.warning(
                            "&nbsp; Invalid Credentials. Please try again.", icon="⚠️"
                        )
                        time.sleep(5)
                        authentication_failed_alert.empty()

        st.markdown(
            "<BR><BR><BR><BR><BR><center><font color='grey'>Copyright © 2024 BeyondML. All Rights Reserved.</font></center>",
            unsafe_allow_html=True,
        )

    else:
        with st.sidebar:
            selected_menu_item = sac.menu(
                [
                    sac.MenuItem(
                        "Booking Management",
                        icon="grid",
                    ),
                    sac.MenuItem(
                        "Explore and Edit Halls",
                        icon="house-add",
                    ),
                    sac.MenuItem(" ", disabled=True),
                    sac.MenuItem(type="divider"),
                ],
                open_all=True,
            )

        if selected_menu_item == "Booking Management":
            st.markdown(
                "<H2 style='color: #ffffff;'>Booking Management</H2>",
                unsafe_allow_html=True,
            )

            st.markdown(
                "<P align='justify'>Welcome to the Admin Console of SeminarSpace! Here, you have complete control over all booking requests, ensuring smooth operation & efficient resource allocation. Review pending requests and instantly approve or reject booking requests in a single tap</P>",
                unsafe_allow_html=True,
            )

            selected_tab = sac.tabs(
                [
                    sac.TabsItem(
                        label="Pending Requests",
                    ),
                    sac.TabsItem(
                        label="Request History",
                    ),
                ],
                align="left",
                variant="outline",
            )

            if selected_tab == "Pending Requests":
                custom_query = CustomQuery("database/seminarspace.db")
                try:
                    pending_booking_requests = (
                        custom_query.fetch_booking_requests_by_booking_status(
                            is_pending=True, sorted_in_asc=True
                        )
                    )
                except: pending_booking_requests = []

                with st.sidebar.expander("Check Conflicting Bookings"):
                    halls_utils = HallsUtils("database/seminarspace.db")
                    try:
                        available_halls = halls_utils.retrieve_records()

                        dict_available_halls = {}

                        for (
                            hall_id,
                            hall_name,
                            capacity,
                            description,
                            hall_image_url,
                        ) in available_halls:
                            dict_key = hall_name
                            dict_available_halls[dict_key] = [
                                hall_id,
                                hall_name,
                                capacity,
                                description,
                                hall_image_url,
                            ]

                        seminar_hall_names = dict_available_halls.keys()

                        input_seminar_hall = st.selectbox(
                            "Select the hall:",
                            seminar_hall_names,
                            label_visibility="collapsed",
                        )

                        selected_hall_details = dict_available_halls[input_seminar_hall]
                        selected_hall_id = selected_hall_details[0]
                        selected_hall_image_url = selected_hall_details[4]

                        cola, colb = st.columns(2)

                        with cola:
                            conflict_check_start_date = st.date_input(
                                "Start Date",
                                value="today",
                                label_visibility="visible",
                                format="YYYY-MM-DD",
                            )
                        with colb:
                            conflict_check_end_date = st.date_input(
                                "End Date",
                                value="today",
                                label_visibility="visible",
                                format="YYYY-MM-DD",
                            )

                        custom_query = CustomQuery("database/seminarspace.db")
                        booking_conflicts = custom_query.fetch_bookings_between_dates(
                            selected_hall_id,
                            conflict_check_start_date,
                            conflict_check_end_date,
                        )

                        if len(booking_conflicts) > 0:
                            sac.divider(
                                label="Collisions",
                                icon="house",
                                align="center",
                                color="grey",
                            )

                            for booking in booking_conflicts:
                                booking_id, start_date, end_date, status = (
                                    booking[0],
                                    booking[4],
                                    booking[5],
                                    booking[7],
                                )

                                start_date_mmm_dd = datetime.strptime(
                                    start_date, "%Y-%m-%d"
                                ).strftime("%b %d")
                                end_date_mmm_dd = datetime.strptime(
                                    end_date, "%Y-%m-%d"
                                ).strftime("%b %d")

                                col1, col2 = st.columns([1, 3])

                                with col1:
                                    st.image(
                                        Image.open(selected_hall_image_url).resize(
                                            (225, 207)
                                        ),
                                        use_column_width=True,
                                    )

                                with col2:
                                    st.markdown(
                                        f"<p><B>Booking Id: {booking_id}</B><BR>{start_date_mmm_dd} - {end_date_mmm_dd} &nbsp;•&nbsp; {status}</p>",
                                        unsafe_allow_html=True,
                                    )

                                if (
                                    booking_conflicts.index(booking)
                                    != len(booking_conflicts) - 1
                                ):
                                    sac.divider(
                                        align="center",
                                        color="grey",
                                        key="_divider_" + booking_id,
                                    )

                        else:
                            st.markdown(" ", unsafe_allow_html=True)
                            sac.result(
                                label="All Good to Go!",
                                description="No conflicting bookings found",
                                status="empty",
                                icon=sac.BsIcon(name="house", size=55, color=None),
                            )
                    except: pass

                if len(pending_booking_requests) == 0:
                    st.markdown("<BR><BR>", unsafe_allow_html=True)
                    sac.result(
                        label="All Caught Up",
                        description="New requests will show up here",
                        status="empty",
                    )

                for pending_requests in pending_booking_requests:
                    booking_id = pending_requests[0]

                    requested_on = pending_requests[3]
                    start_date = pending_requests[4]
                    end_date = pending_requests[5]

                    booking_justification = pending_requests[6]
                    status = pending_requests[7]

                    if len(booking_justification) > 113:
                        booking_justification = booking_justification[:111] + "..."

                    user_id = pending_requests[1]
                    user_full_name = fetch_user_full_name_by_username(user_id)

                    hall_id = pending_requests[2]
                    custom_query = CustomQuery("database/seminarspace.db")
                    hall_details = custom_query.fetch_hall_details_by_hall_id(hall_id)

                    hall_name = hall_details[1]
                    hall_image_url = hall_details[4]

                    col_hall_image, col_title, _, col_cta = st.columns(
                        [1.45, 3, 0.01, 2]
                    )

                    with col_hall_image:
                        st.image(Image.open(hall_image_url).resize((225, 215)))

                    with col_title:
                        st.markdown(
                            f"<B>Booking Id: </B>{booking_id}",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<H3>{hall_name}</H3>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<p align='justify'>Request raised by {user_full_name} on {requested_on}.<br>{booking_justification}</p>",
                            unsafe_allow_html=True,
                        )

                    with col_cta:
                        st.write(" ")

                        start_date_mmm_dd = datetime.strptime(
                            start_date, "%Y-%m-%d"
                        ).strftime("%b %d")
                        end_date_mmm_dd = datetime.strptime(
                            end_date, "%Y-%m-%d"
                        ).strftime("%b %d")

                        st.markdown(
                            f"<BR><P align='right' style='padding-bottom: 15px;'><font size=3.5><B>{start_date_mmm_dd} - {end_date_mmm_dd}</B></font></P>",
                            unsafe_allow_html=True,
                        )
                        st.write(" ")

                        col1, col2 = st.columns(2)

                        with col1:
                            _key_approve_button = "approve_" + booking_id
                            button_approve_request = st.button(
                                "Approve",
                                use_container_width=True,
                                key=_key_approve_button,
                            )

                            if button_approve_request:
                                bookings = BookingsUtils("database/seminarspace.db")
                                bookings.update_records(
                                    booking_id, "status", "Approved"
                                )

                                st.toast(f"Booking Id {booking_id} has been approved")
                                time.sleep(3)
                                st.rerun()

                        with col2:
                            _key_reject_button = "reject_" + booking_id
                            button_reject_request = st.button(
                                "Reject",
                                use_container_width=True,
                                key=_key_reject_button,
                            )

                            if button_reject_request:
                                bookings = BookingsUtils("database/seminarspace.db")
                                bookings.update_records(
                                    booking_id, "status", "Rejected"
                                )

                                st.toast(f"Booking Id {booking_id} has been rejected")
                                time.sleep(3)
                                st.rerun()

                    sac.divider(align="center", color="#1c1c1c", key=booking_id)

                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>", unsafe_allow_html=True
                )
                st.sidebar.markdown(" ", unsafe_allow_html=True)

                button_logout_admin_console = st.sidebar.button(
                    "Logout from Admin Console", use_container_width=True
                )

                if button_logout_admin_console:
                    st.session_state.admin_authentication_status = None
                    st.rerun()

                st.markdown(" ", unsafe_allow_html=True)
                st.markdown(" ", unsafe_allow_html=True)

            if selected_tab == "Request History":
                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>",
                    unsafe_allow_html=True,
                )
                button_logout_admin_console = st.sidebar.button(
                    "Logout from Admin Console", use_container_width=True
                )

                if button_logout_admin_console:
                    st.session_state.admin_authentication_status = None
                    st.rerun()

                custom_query = CustomQuery("database/seminarspace.db")
                try:
                    pending_booking_requests = (
                        custom_query.fetch_booking_requests_by_booking_status(
                            is_pending=False, sorted_in_asc=False
                        )
                    )
                except: pending_booking_requests = []

                if len(pending_booking_requests) == 0:
                    st.markdown("<BR><BR>", unsafe_allow_html=True)
                    sac.result(
                        label="No Bookings Yet",
                        description="Sit back soon to see new requests",
                        status="empty",
                    )

                for pending_requests in pending_booking_requests:
                    booking_id = pending_requests[0]

                    requested_on = pending_requests[3]
                    start_date = pending_requests[4]
                    end_date = pending_requests[5]

                    status = pending_requests[7]

                    booking_justification = pending_requests[6]
                    if len(booking_justification) > 113:
                        booking_justification = booking_justification[:113] + "..."

                    user_id = pending_requests[1]
                    user_full_name = fetch_user_full_name_by_username(user_id)

                    hall_id = pending_requests[2]
                    custom_query = CustomQuery("database/seminarspace.db")
                    hall_details = custom_query.fetch_hall_details_by_hall_id(hall_id)

                    hall_name = hall_details[1]
                    hall_image_url = hall_details[4]

                    col_hall_image, col_title, _, col_cta = st.columns(
                        [1.45, 3.4, 0.01, 1.75]
                    )

                    with col_hall_image:
                        st.image(Image.open(hall_image_url).resize((225, 222)))

                    with col_title:
                        st.markdown(
                            f"<B>Booking Id: </B>{booking_id}",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<H3>{hall_name}</H3>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<p align='justify'>Request raised by {user_full_name} on {requested_on}.<br>{booking_justification}</p>",
                            unsafe_allow_html=True,
                        )

                    with col_cta:
                        st.write(" ")

                        start_date_mmm_dd = datetime.strptime(
                            start_date, "%Y-%m-%d"
                        ).strftime("%b %d")
                        end_date_mmm_dd = datetime.strptime(
                            end_date, "%Y-%m-%d"
                        ).strftime("%b %d")

                        st.markdown(
                            f"<BR><P align='right' style='padding-bottom: 15px;'><font size=4><B>{start_date_mmm_dd} - {end_date_mmm_dd}</B></font></P>",
                            unsafe_allow_html=True,
                        )
                        st.write(" ")

                        if status.lower() == "pending":
                            display_status = "Pending Approval"

                        elif status.lower() == "rejected":
                            display_status = "Request Rejected"

                        elif status.lower() == "approved":
                            display_status = "Booking Approved"

                        else:
                            display_status = "Unknown"

                        st.markdown(
                            f"<H4 align='right' style='padding-top: 12px;'><B>{display_status}</B></H4>",
                            unsafe_allow_html=True,
                        )

                    # sac.divider(align='center', color='#1c1c1c', key=booking_id)
                    if (
                        pending_booking_requests.index(pending_requests)
                        != len(pending_booking_requests) - 1
                    ):
                        st.markdown(" ", unsafe_allow_html=True)

                st.markdown(" ", unsafe_allow_html=True)
                st.markdown(" ", unsafe_allow_html=True)

        else:
            st.markdown(
                "<H2 style='color: #ffffff;'>Add/Edit Seminar Halls</H2>",
                unsafe_allow_html=True,
            )

            st.markdown(
                "<P align='justify'> This page is your hub for adding new halls, updating existing ones, and ensuring every space is optimized for a seamless user experience. Define available booking times, minimum booking duration and any cancellation policies, along with the hall layouts!</P>",
                unsafe_allow_html=True,
            )

            # with st.sidebar:
            selected_tab_edit_page = sac.tabs(
                [
                    sac.TabsItem(
                        label="Add New Hall",
                    ),
                    sac.TabsItem(
                        label="Update Hall Details",
                    ),
                ],
                align="left",
                variant="outline",
            )

            if selected_tab_edit_page == "Add New Hall":
                halls_utils = HallsUtils("database/seminarspace.db")

                with st.form("form_add_new_hall"):
                    col1, col2 = st.columns([1, 2.5])
                    with col1:
                        hall_name = st.text_input(
                            "Enter the Hall Name", placeholder="Hall name"
                        )
                        hall_id = "hall_" + str(uuid.uuid4())[:4].lower()

                        st.text_input(
                            "Hall Id",
                            label_visibility="collapsed",
                            value="Hall Id: " + hall_id,
                            disabled=True,
                        )
                        hall_capacity = st.number_input("Enter Total Capacity", step=10)

                    with col2:
                        hall_img_url = st.text_input(
                            "Enter Image URL",
                            placeholder="Path to image (eg: assets/images/halls/...)",
                        )
                        hall_description = st.text_area(
                            "Enter Description",
                            placeholder="Briefly mention any restrictions or policies related to using the hall",
                        )

                    hall_layout = st.file_uploader(
                        "Choose a file",
                        type=["pdf"],
                        label_visibility="collapsed",
                        help="Upload hall layout",
                    )
                    col1, col2 = st.columns([1, 2.5])

                    with col2:
                        cola, colb = st.columns([1.5, 1])

                        with cola:
                            checkbox_create_hall = st.checkbox(
                                "Create hall and make it available for booking.",
                                value=True,
                            )
                        with colb:
                            st.checkbox("Send email update to users")

                    with col1:
                        button_submit_add_new_hall_form = st.form_submit_button(
                            "Add New Hall", use_container_width=True
                        )

                    if button_submit_add_new_hall_form:
                        if (
                            (len(hall_name) < 1)
                            or (hall_capacity < 10)
                            or (len(hall_img_url) < 1)
                            or (len(hall_description) < 1)
                        ):
                            st.toast("Fill all necessary fields")

                        else:
                            try:
                                if checkbox_create_hall is True:
                                    halls = HallsUtils("database/seminarspace.db")

                                    hall_details = tuple(
                                        (
                                            hall_id,
                                            hall_name,
                                            hall_capacity,
                                            hall_description,
                                            hall_img_url,
                                        )
                                    )
                                    halls.insert_records(hall_details)

                                    try:
                                        with open(
                                            f"assets/hall_layouts/layout_{hall_id}.pdf)",
                                            "wb",
                                        ) as hall_layout_file:
                                            hall_layout_file.write(
                                                hall_layout.getbuffer()
                                            )
                                    except:
                                        pass

                                    st.toast("Hall created successfully")
                                    success_add_new_hall = st.success(
                                        f"{hall_name} is now available for booking",
                                        icon="✅",
                                    )
                                    time.sleep(4)

                                    success_add_new_hall.empty()
                                    time.sleep(1)
                                    st.rerun()

                                elif checkbox_create_hall is False:
                                    st.toast(
                                        "Tap the checkbox to agree and continue creating the hal"
                                    )

                            except Exception as error:
                                exception_add_new_hall = st.warning(
                                    "Unable to save the new hall. Contact support if the issue persists.",
                                    icon="⚠️",
                                )
                                time.sleep(4)
                                exception_add_new_hall.empty()

                    st.sidebar.markdown(
                        "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>",
                        unsafe_allow_html=True,
                    )
                    button_logout_admin_console = st.sidebar.button(
                        "Logout from Admin Console", use_container_width=True
                    )

                    if button_logout_admin_console:
                        st.session_state.admin_authentication_status = None
                        st.rerun()

                st.markdown(" ", unsafe_allow_html=True)
                st.markdown(" ", unsafe_allow_html=True)

            else:
                halls_utils = HallsUtils("database/seminarspace.db")
                available_halls = halls_utils.retrieve_records()

                if len(available_halls) <= 0:
                    st.markdown("<BR><BR>", unsafe_allow_html=True)
                    sac.result(
                        label="No Halls Available",
                        description="Your halls will show up here",
                        status="empty",
                    )

                dict_available_halls = {}
                for (
                    hall_id,
                    hall_name,
                    capacity,
                    description,
                    hall_image_url,
                ) in available_halls:
                    dict_key = hall_name
                    dict_available_halls[dict_key] = [
                        hall_id,
                        hall_name,
                        capacity,
                        description,
                        hall_image_url,
                    ]

                # seminar_hall_names = [value[0] for value in dict_available_halls.values()]
                seminar_hall_names = dict_available_halls.keys()

                input_seminar_hall = st.sidebar.selectbox(
                    "Select hall to edit:",
                    seminar_hall_names,
                )

                if input_seminar_hall:
                    selected_hall_details = dict_available_halls[input_seminar_hall]
                    (
                        current_hall_id,
                        current_hall_name,
                        current_capacity,
                        current_hall_description,
                        current_hall_image_url,
                    ) = (
                        selected_hall_details[0],
                        selected_hall_details[1],
                        selected_hall_details[2],
                        selected_hall_details[3],
                        selected_hall_details[4],
                    )

                    container = st.container(border=True)
                    col1, col2 = container.columns([2.5, 1])

                    with col2:
                        current_hall_id = st.text_input(
                            "Hall Id", value=current_hall_id, disabled=True
                        )

                        try:
                            st.image(Image.open(hall_img_url).resize((237, 219)))
                        except:
                            st.image(
                                Image.open(current_hall_image_url).resize((237, 219))
                            )

                    with col1:
                        hall_name = st.text_input(
                            "Enter the Hall Name", value=current_hall_name
                        )

                        col3, col4 = st.columns(2)

                        with col3:
                            hall_capacity = st.number_input(
                                "Enter Total Capacity", value=current_capacity
                            )

                        with col4:
                            hall_img_url = st.text_input(
                                "Enter Image URL", value=current_hall_image_url
                            )

                        hall_description = st.text_area(
                            "Enter Description", value=current_hall_description
                        )

                        col4, col5, col3 = st.columns([1.5, 1.5, 2])

                        with col4:
                            button_update_hall = st.button(
                                "Update Hall Details", use_container_width=True
                            )
                            if button_update_hall:
                                if (
                                    (len(hall_name) < 1)
                                    or (hall_capacity < 10)
                                    or (len(hall_img_url) < 1)
                                    or (len(hall_description) < 1)
                                ):
                                    st.toast("Fill all necessary fields")
                                else:
                                    halls = HallsUtils("database/seminarspace.db")

                                    halls.update_records(
                                        current_hall_id, "hall_name", hall_name
                                    )
                                    halls.update_records(
                                        current_hall_id, "capacity", hall_capacity
                                    )
                                    halls.update_records(
                                        current_hall_id, "description", hall_description
                                    )
                                    halls.update_records(
                                        current_hall_id, "img_url", hall_img_url
                                    )

                                    st.toast(f"Successfully updated {hall_name}")
                                    time.sleep(3)
                                    st.rerun()

                        with col5:
                            button_delete_hall = st.button(
                                "Delete Seminar Hall", use_container_width=True
                            )
                            if button_delete_hall:
                                halls = HallsUtils("database/seminarspace.db")
                                halls.delete_records(current_hall_id)

                                st.toast(f"Successfully deleted {hall_name}")
                                time.sleep(3)
                                st.rerun()

                st.markdown(" ", unsafe_allow_html=True)
                st.markdown(" ", unsafe_allow_html=True)

                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>", unsafe_allow_html=True
                )
                button_logout_admin_console = st.sidebar.button(
                    "Logout from Admin Console", use_container_width=True
                )

                if button_logout_admin_console:
                    st.session_state.admin_authentication_status = None
                    st.rerun()
