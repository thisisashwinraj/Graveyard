import time
import uuid
from PIL import Image
from datetime import date, datetime
import streamlit as st
import streamlit_antd_components as sac

from database.db_utils import BookingsUtils, HallsUtils, CustomQuery

from database.firebase import (
    login_form,
    signup_form,
    reset_password_form,
    logout_button,
    fetch_user_full_name_by_username,
)
from pages.your_booking_requests import BookingRequests


st.set_page_config(
    page_title="SeminarSpace",
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
    if "user_authentication_status" not in st.session_state:
        st.session_state.user_authentication_status = None

    if "authenticated_user_email_id" not in st.session_state:
        st.session_state.authenticated_user_email_id = None

    if "authenticated_user_username" not in st.session_state:
        st.session_state.authenticated_user_username = None

    if st.session_state.user_authentication_status is not True:
        with st.sidebar:
            selected_menu_item = sac.menu(
                [
                    sac.MenuItem(
                        "LogIn to Your Account",
                        icon="grid",
                    ),
                    sac.MenuItem(
                        "Register New Account",
                        icon="house-add",
                    ),
                    sac.MenuItem(" ", disabled=True),
                    sac.MenuItem(type="divider"),
                ],
                open_all=True,
            )

        if selected_menu_item == "LogIn to Your Account":
            login_form()
            reset_password_form()

            st.markdown(
                "<H2>Welcome to SeminarSpace</H2>",
                unsafe_allow_html=True,
            )

        elif selected_menu_item == "Register New Account":
            signup_form()

    else:
        with st.sidebar:
            selected_menu_item = sac.menu(
                [
                    sac.MenuItem(
                        "SeminarSpace - Home",
                        icon="grid",
                    ),
                    sac.MenuItem(
                        "Manage Your Bookings",
                        icon="house-add",
                    ),
                    sac.MenuItem(" ", disabled=True),
                    sac.MenuItem(type="divider"),
                ],
                open_all=True,
            )

        if selected_menu_item == "SeminarSpace - Home":
            st.markdown(
                f"<H2>Hey There, {fetch_user_full_name_by_username(st.session_state.authenticated_user_username)}</H2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<P align='justify'>Welcome to SeminarSpace, your one-stop shop for booking the perfect space for your next big event. Whether you're planning a 3 day workshop, a collaborative brainstorm or an epic study session, we've got you covered with a variety of halls from your campus</A></P>",
                unsafe_allow_html=True,
            )

            tab_explore_seminar_halls = sac.tabs(
                [
                    sac.TabsItem(label="Explore Seminar Halls"),
                    sac.TabsItem(label="Available Halls"),
                ],
                variant="outline",
            )

            if tab_explore_seminar_halls == "Explore Seminar Halls":
                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>",
                    unsafe_allow_html=True,
                )
                logout_button()

                hall_utils = HallsUtils("database/seminarspace.db")
                available_seminar_halls = hall_utils.retrieve_records()

                if len(available_seminar_halls) < 1:
                    st.markdown("<BR><BR>", unsafe_allow_html=True)
                    sac.result(
                        label="No Halls Available",
                        description="Available halls will show up here",
                        status="empty",
                    )

                container_1, container_2, container_3, container_4 = st.columns(4)

                for hall in available_seminar_halls:
                    idx_hall = available_seminar_halls.index(hall)

                    if idx_hall in [0, 4, 8, 12, 16]:
                        container = container_1

                    elif idx_hall in [1, 5, 9, 13, 17]:
                        container = container_2

                    elif idx_hall in [2, 6, 10, 14, 18]:
                        container = container_3

                    elif idx_hall in [3, 7, 11, 15, 19]:
                        container = container_4

                    else:
                        break

                    (
                        hall_id,
                        hall_name,
                        hall_capacity,
                        hall_description,
                        hall_image_url,
                    ) = (hall[0], hall[1], hall[2], hall[3], hall[4])

                    with container:
                        st.image(Image.open(hall_image_url))

                        st.markdown(f"<H5>{hall_name}</H5>", unsafe_allow_html=True)
                        st.markdown(
                            f"<p style='font-size: 16px;'><B>Seating Capacity:</B> {hall_capacity} Persons<BR>Explore layout for more details",
                            unsafe_allow_html=True,
                        )

                        try:
                            button_download_layout = st.download_button(
                                "Download Hall Layout",
                                data=open(
                                    f"assets/hall_layouts/layout_{hall_id}.pdf", "rb"
                                ).read(),
                                file_name=f"{hall_name} Layout.pdf",
                                use_container_width=True,
                                key=f"download_button_{hall_id}",
                            )

                        except:
                            if st.button(
                                f"Download Hall Layout",
                                use_container_width=True,
                                key=f"button_{hall_id}",
                            ):
                                st.toast(f"Layout for {hall_name} is not available")

                        st.markdown(
                            " ",
                            unsafe_allow_html=True,
                        )

            else:
                availability_start_date = str(
                    st.sidebar.date_input(
                        "Select Start Date",
                        value="today",
                        label_visibility="visible",
                        format="YYYY-MM-DD",
                    )
                )
                availability_end_date = str(
                    st.sidebar.date_input(
                        "Select End Date",
                        value="today",
                        label_visibility="visible",
                        format="YYYY-MM-DD",
                    )
                )

                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR>",
                    unsafe_allow_html=True,
                )
                st.sidebar.markdown(
                    " ",
                    unsafe_allow_html=True,
                )
                logout_button()

                custom_query = CustomQuery("database/seminarspace.db")
                try:
                    available_seminar_halls = (
                        custom_query.fetch_available_halls_between_dates(
                            availability_start_date, availability_end_date
                        )
                    )
                except: available_seminar_halls = []

                if len(available_seminar_halls) < 1:
                    st.markdown("<BR><BR>", unsafe_allow_html=True)
                    sac.result(
                        label="No Halls Available",
                        description="Available halls will show up here",
                        status="empty",
                    )

                container_1, container_2, container_3, container_4 = st.columns(4)

                for hall in available_seminar_halls:
                    idx_hall = available_seminar_halls.index(hall)

                    if idx_hall in [0, 4, 8, 12, 16]:
                        container = container_1

                    elif idx_hall in [1, 5, 9, 13, 17]:
                        container = container_2

                    elif idx_hall in [2, 6, 10, 14, 18]:
                        container = container_3

                    elif idx_hall in [3, 7, 11, 15, 19]:
                        container = container_4

                    else:
                        break

                    (
                        hall_id,
                        hall_name,
                        hall_capacity,
                        hall_description,
                        hall_image_url,
                    ) = (hall[0], hall[1], hall[2], hall[3], hall[4])

                    with container:
                        st.image(Image.open(hall_image_url))

                        st.markdown(f"<H5>{hall_name}</H5>", unsafe_allow_html=True)
                        st.markdown(
                            f"<p style='font-size: 16px;'><B>Seating Capacity:</B> {hall_capacity} Persons<BR>Explore layout for more details",
                            unsafe_allow_html=True,
                        )

                        try:
                            button_download_layout = st.download_button(
                                "Download Hall Layout",
                                data=open(
                                    f"assets/hall_layouts/layout_{hall_id}.pdf", "rb"
                                ).read(),
                                file_name=f"{hall_name} Layout.pdf",
                                use_container_width=True,
                                key=f"download_button_{hall_id}",
                            )
                        except:
                            if st.button(
                                f"Download Hall Layout",
                                use_container_width=True,
                                key=f"button_{hall_id}",
                            ):
                                st.toast(f"Layout for {hall_name} is not available")

                        st.markdown(
                            " ",
                            unsafe_allow_html=True,
                        )

            usage_caution_message = """
            **SeminarSpace Offers You More Than Just Booking!**

            We're your partner in creating successful events. Our intuitive interface makes finding and booking halls a breeze. So whether you need a small, intimate room or a spacious auditorium, we have the perfect fit for you. Ready to book your next big event? Let's make it amazing! Browse our curated list of seminar halls, secure your space & focus on creating an unforgettable event!
            """
            st.info(usage_caution_message)

            st.markdown(
                "<H3>Recent Booking Requests</H3>",
                unsafe_allow_html=True,
            )

            st.markdown(
                "<P align='justify'>This section shows your recent booking requests. Check out the Booking History section on Manage Bookings page for a complete overview. Have questions for us? Our support team is always happy to help. Simply drop us a line & we'll get back to you in a flash!</A></P>",
                unsafe_allow_html=True,
            )
            st.markdown(
                " ",
                unsafe_allow_html=True,
            )

            try:
                custom_query = CustomQuery("database/seminarspace.db")
                try:
                    pending_booking_requests = (
                        custom_query.fetch_booking_requests_by_username(
                            st.session_state.authenticated_user_username, "DESC"
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

                for pending_requests in pending_booking_requests[:2]:
                    booking_id = pending_requests[0]

                    requested_on = pending_requests[3]
                    start_date = pending_requests[4]
                    end_date = pending_requests[5]

                    status = pending_requests[7]
                    booking_justification = pending_requests[6]
                    if len(booking_justification) > 113:
                        booking_justification = booking_justification[:116] + "..."

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

                    if pending_booking_requests.index(pending_requests) < 1:
                        st.markdown(" ", unsafe_allow_html=True)
                    else:
                        st.markdown("<BR>", unsafe_allow_html=True)

            except Exception as page_error:
                st.sidebar.write(page_error)

        elif selected_menu_item == "Manage Your Bookings":
            st.markdown(
                "<H2 style='color: #ffffff;'>Manage Your Bookings</H2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<P align='justify'>Ready to ignite your seminar magic? Find the perfect space for your event, from collaborative brainstorming sessions to epic study groups right here on SeminarSpace! No matter your vision, we offer a diverse range of open halls & auditoriums to make it happen</A></P>",
                unsafe_allow_html=True,
            )

            tab_bookings_page = sac.tabs(
                [
                    sac.TabsItem(label="Book a New Hall"),
                    sac.TabsItem(label="Booking History"),
                ],
                variant="outline",
            )

            if tab_bookings_page == "Book a New Hall":
                container = st.container(border=True)

                col_1, col_2 = container.columns([2, 1])

                with col_1:
                    input_event_name = st.text_input(
                        "Enter your event's name:",
                        placeholder="Enter your event name",
                    )

                    col_start_date, col_end_date = st.columns(2)

                    with col_start_date:
                        input_start_date = st.date_input(
                            "Select booking start date:",
                            value="today",
                            label_visibility="visible",
                        )
                    with col_end_date:
                        input_end_date = st.date_input(
                            "Select booking end date:",
                            value="today",
                            label_visibility="visible",
                        )

                    custom_query = CustomQuery("database/seminarspace.db")
                    try:
                        available_seminar_halls = (
                            custom_query.fetch_available_halls_between_dates(
                                input_start_date, input_end_date
                            )
                        )
                    except: available_seminar_halls = []

                    hall_lookup_dict = {}

                    for hall_id, hall_name, _, _, _ in available_seminar_halls:
                        hall_lookup_dict[hall_id] = hall_name

                    input_hall_name = st.selectbox(
                        "Select your prefered hall:",
                        list(hall_lookup_dict.values()),
                        label_visibility="collapsed",
                    )
                    try:
                        input_hall_id = [
                            key
                            for key, value in hall_lookup_dict.items()
                            if value == input_hall_name
                        ][0]
                    except:
                        input_hall_id = None

                with col_2:
                    # st.write(available_seminar_halls)
                    booking_id = "book" + str(uuid.uuid4())[:4].lower()
                    booking_id_text_input = st.text_input(
                        " ",
                        placeholder=f"{booking_id}",
                        label_visibility="hidden",
                        disabled=True,
                    )

                    input_booking_justification = st.text_area(
                        "Tell us about your event:",
                        placeholder="Tell us about the seminar, expected head count, & required equpiments",
                    )

                if input_hall_id:
                    with st.sidebar.expander("Dislay Hall Details"):
                        custom_query = CustomQuery("database/seminarspace.db")

                        hall_details = custom_query.fetch_hall_details_by_hall_id(
                            input_hall_id
                        )
                        (
                            sidebar_hall_name,
                            sidebar_hall_capacity,
                            sidebar_hall_description,
                            sidebar_hall_image_url,
                        ) = (
                            hall_details[1],
                            hall_details[2],
                            hall_details[3],
                            hall_details[4],
                        )

                        st.image(Image.open(sidebar_hall_image_url))
                        st.markdown(
                            f"<H4>{sidebar_hall_name} ({sidebar_hall_capacity} Seats)</H4>",
                            unsafe_allow_html=True,
                        )

                        if len(sidebar_hall_description) > 35:
                            sidebar_hall_description = sidebar_hall_description[:37]

                        st.markdown(
                            f"<p style='font-size: 16px;'>{sidebar_hall_description}",
                            unsafe_allow_html=True,
                        )

                with col_1:
                    cola, _ = st.columns([1.3, 1.75])
                    with cola:
                        button_book_hall = st.button(
                            "Book Seminar Hall", use_container_width=True
                        )

                if button_book_hall:
                    if (len(input_event_name) < 1) or (
                        len(input_booking_justification) < 1
                    ):
                        st.toast("Fill all necessary fields")

                    elif input_start_date > input_end_date:
                        st.toast("Invalid value for booking dates!")
                        time.sleep(1)
                        st.toast(
                            "Booking end date can not be behind the booking start date."
                        )

                    elif (
                        str(input_start_date) <= str(date.today().strftime("%Y-%m-%d"))
                    ) or (
                        str(input_end_date) <= str(date.today().strftime("%Y-%m-%d"))
                    ):
                        st.toast("The date you selected has already passed!")
                        time.sleep(1)
                        st.toast("Please choose a future date for your booking.")

                    else:
                        try:
                            user_id = st.session_state.authenticated_user_username
                            hall_id = input_hall_id

                            requested_on = date.today().strftime("%Y-%m-%d")
                            start_date = input_start_date
                            end_date = input_end_date

                            purpose = (
                                input_event_name + ": " + input_booking_justification
                            )
                            status = "Pending"

                            booking_utils = BookingsUtils("database/seminarspace.db")
                            booking_utils.insert_records(
                                (
                                    booking_id,
                                    user_id,
                                    hall_id,
                                    requested_on,
                                    start_date,
                                    end_date,
                                    purpose,
                                    status,
                                )
                            )
                            booking_confirmed_message = st.success("Booking confirmed")
                            time.sleep(5)
                            booking_confirmed_message.empty()

                        except Exception as error:
                            st.toast("Unable to book now. Try again later!")

                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>",
                    unsafe_allow_html=True,
                )
                st.sidebar.markdown(
                    " ",
                    unsafe_allow_html=True,
                )
                logout_button()

            else:
                try:
                    custom_query = CustomQuery("database/seminarspace.db")
                    try:
                        pending_booking_requests = (
                            custom_query.fetch_booking_requests_by_username(
                                st.session_state.authenticated_user_username, "DESC"
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
                            booking_justification = booking_justification[:116] + "..."

                        user_id = pending_requests[1]
                        user_full_name = fetch_user_full_name_by_username(user_id)

                        hall_id = pending_requests[2]
                        custom_query = CustomQuery("database/seminarspace.db")
                        hall_details = custom_query.fetch_hall_details_by_hall_id(
                            hall_id
                        )

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

                except Exception as page_error:
                    st.sidebar.write(page_error)
                st.markdown("<BR>", unsafe_allow_html=True)

                st.sidebar.markdown(
                    "<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>",
                    unsafe_allow_html=True,
                )
                logout_button()
