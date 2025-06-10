import * as React from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.min.css'


const DatePick = (props: {
    startDate: Date | null;
    endDate: Date | null;
    onDateChange: (dates: [Date | null, Date | null]) => void;
}) => {

    return (
        <DatePicker
            className="custom-datepicker"
            selected={props.startDate}
            onChange={props.onDateChange}
            startDate={props.startDate}
            endDate={props.endDate}
            selectsRange
            placeholderText="select date interval..."
            isClearable
        />
    );
};

export default DatePick;