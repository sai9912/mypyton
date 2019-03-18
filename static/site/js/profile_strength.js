function fillMeter(percent) {
    var pixels = (percent / 100) * 90;
    $(".fill").css('top', (90 - pixels) + "px");
    $(".fill").css('height', pixels + "px");
    $(".line").css('top', (90 - pixels) + "px");

    switch (true) {
        case (percent >= 66 && percent <= 100):
            $(".line div").text(gettext('Strong'));
            break;
        case (percent >= 33 && percent < 66):
            $(".line div").text(gettext('Medium'));
            break;
        case (percent >= 0 && percent < 33):
            $(".line div").text(gettext('Weak'));
            break;
        default:
            $(".line div").text(gettext('Weak'));
            break;
    }
}
