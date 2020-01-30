from gui.guiComponent import *
import time
class PriceInfo(GuiComponent):
    def __init__(self):
        super().__init__()
        self.price = []
        self.price_vals = []
        self.avg_times = []
        self.opened = time.time()
        self.elapsed = 0
    def add_price_info(self, price, price_vals, avg_times):
        if not self.is_closed():
            self.close()
        self.opened = time.time()
        self.price = price
        self.price_vals = price_vals
        self.avg_times = avg_times
    def should_close(self):
        if self.is_closed():
            return
        self.elapsed = time.time() - self.opened
        if self.elapsed >= 3:
            elapsed = 0
            self.close()
    def add_components(self):
        # Setting up Master Frame, only currently used for background color due to grid format.
        masterFrame = Frame(self.frame, bg="#1f1f1f")
        masterFrame.place(relwidth=1, relheight=1)

        spacerLabel = Label(self.frame, text="   ", bg="#0d0d0d")
        spacerLabel.grid(column=0, row=0, columnspan=3, sticky="w" + "e")

        # Setting up header row of labels.
        bglabel = Label(self.frame, bg="#0d0d0d").grid(column=0, row=1, columnspan=3, sticky="w" + "e")
        headerLabel = Label(self.frame, text="Listed Price:", bg="#0d0d0d", fg="#e6b800").grid(column=0, row=1, padx=5)
        headerLabel2 = Label(self.frame, text="Avg. Time Listed:", bg="#0d0d0d", fg="#e6b800").grid(
            column=2, row=1, padx=5
        )
        headerLabel3 = Label(self.frame, text="   ", bg="#0d0d0d", fg="#e6b800").grid(column=1, row=1, sticky="w" + "e")
        rows_used = len(self.price_vals)

        for row in range(rows_used):
            days = self.avg_times[row][0]
            if days > 0:
                days = str(days) + " days, "
            else:
                days = None

            hours = None
            if self.avg_times[row][1] > 3600:
                hours = str(round(self.avg_times[row][1] / 3600, 2)) + " hours"
            else:
                hours = "< 1 hour"

            if days is not None:
                avg_time_text = days + hours
            else:
                avg_time_text = hours

            # Alternates row color.
            if row % 2 == 0:
                # Needed here because other color is consistent with canvas color.
                bgAltLabel = Label(self.frame, bg="#1a1a1a").grid(column=0, row=2 + row, columnspan=3, sticky="w" + "e")
                priceLabel = Label(self.frame, text=self.price_vals[row], bg="#1a1a1a", fg="#e6b800").grid(
                    column=0, row=2 + row, sticky="w", padx=5
                )
                avgTimeLabel = Label(self.frame, text=avg_time_text, bg="#1a1a1a", fg="#e6b800").grid(
                    column=2, row=2 + row, sticky="w", padx=5
                )
            else:
                priceLabel = Label(self.frame, text=self.price_vals[row], bg="#1f1f1f", fg="#e6b800").grid(
                    column=0, row=2 + row, sticky="w", padx=5
                )
                avgTimeLabel = Label(self.frame, text=avg_time_text, bg="#1f1f1f", fg="#e6b800").grid(
                    column=2, row=2 + row, sticky="w", padx=5
                )

            footerbgLabel = Label(self.frame, bg="#0d0d0d").grid(column=0, row=rows_used + 3, columnspan=3, sticky="w" + "e")

            minPriceLabel = Label(self.frame, text="Low: " + str(self.price[0]), bg="#0d0d0d", fg="#e6b800")
            minPriceLabel.grid(column=0, row=rows_used + 3, padx=10)

            avgPriceLabel = Label(self.frame, text="Avg: " + str(self.price[1]), bg="#0d0d0d", fg="#e6b800")
            avgPriceLabel.grid(column=1, row=rows_used + 3, padx=10)

            maxPriceLabel = Label(self.frame, text="High: " + str(self.price[2]), bg="#0d0d0d", fg="#e6b800")
            maxPriceLabel.grid(column=2, row=rows_used + 3, padx=10)
"""
gui = PriceInfo()
gui.show(0,10)

gui2 = GuiComponent()
gui2.show(0,100)
time.sleep(5)
gui.close()
gui.close()
time.sleep(3)
gui2.close()
while True:
    time.sleep(1)
"""