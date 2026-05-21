namespace aktaWP;

public partial class WielkiBrat : Form
{
    private Dictionary<int, string> data = new Dictionary<int, string>()
    {
        {1, "Poszukiwania kaolinu na obszarach polarnych"},
        {2, "Prowadzenia wydobycia cynku w jakiejkolwiek formie"},
        {3, "Tworzenia aplikacji frontendowych w języku Rust"},
        {4, "Poruszania się kabrioletem z otwartym dachem przy prędkości przekraczającej 30 km/h"},
        {5, "Braku powitania „dzień dobry” na klatce schodowej"},
        {6, "Bezpośredniego wykonywania operacji eval na danych zakodowanych w base64 poprzez API"},
        {7, "Jedzenie pierogów z nutella"}
    };
    
    private int AsciiSum(string input)
    {
        int sum = 0;

        foreach (char c in input)
        {
            sum += (int)c;
        }

        return sum;
    }
    public WielkiBrat()
    {
        InitializeComponent();
        SetMode1();
    }

    private void radioButton1_CheckedChanged(object sender, EventArgs e)
    {
        if (radioButton1.Checked)
        {
            SetMode1();
        }
    }

    private void radioButton2_CheckedChanged(object sender, EventArgs e)
    {
        if (radioButton2.Checked)
        {
            SetMode2();
        }
    }
    private void button2_Click(object sender, EventArgs e)
    {
        try
        {
            int id1 = int.Parse(textBox2.Text);
            int id2 = int.Parse(textBox3.Text);

            if (!data.ContainsKey(id1) || !data.ContainsKey(id2))
            {
                MessageBox.Show("Nie ma takiego ID");
                return;
            }

            string value1 = data[id1];
            string value2 = data[id2];
            int sum1 = AsciiSum(value1);
            int sum2 = AsciiSum(value2);

            int result = ((sum1 + sum2)*(sum1+sum2));

            label1.Text = result + " lat więzienia";
        }
        catch
        {
            MessageBox.Show("Błąd danych");
        }
    }
    
    
    private void button1_Click(object sender, EventArgs e)
    {
        try
        {
            int id = int.Parse(textBox1.Text);

            if (!data.ContainsKey(id))
            {
                MessageBox.Show("Nie ma takiego ID");
                return;
            }

            string value = data[id];
            int sum = AsciiSum(value);

            label1.Text = sum + " lat więzienia";
        }
        catch
        {
            MessageBox.Show("Błąd danych");
        }    
    }
    
    private void SetMode1()
    {
        label1.Text = "";
        textBox1.Visible = true;
        label2.Visible = true;
        label3.Visible = false;
        label4.Visible = false;
        textBox2.Visible = false;
        textBox3.Visible = false;
        button2.Visible = false;
    }

    private void SetMode2()
    {
        label3.Visible = true;
        label4.Visible = true;
        textBox1.Visible = false;
        label1.Text = "";
        textBox2.Visible = true;
        textBox3.Visible = true;
        label2.Visible = false;
        button2.Visible = true;
    }
}