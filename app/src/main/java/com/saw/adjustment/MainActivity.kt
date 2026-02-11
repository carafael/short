package com.saw.adjustment

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.textfield.TextInputEditText
class MainActivity : AppCompatActivity() {

    private lateinit var sawView: SawView
    private lateinit var inputPartDiameter: TextInputEditText
    private lateinit var inputSawDiameter: TextInputEditText
    private lateinit var inputRearSlotDepth: TextInputEditText
    private lateinit var inputFrontSlotDepth: TextInputEditText
    private lateinit var btnCalculate: Button
    private lateinit var resultText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sawView = findViewById(R.id.sawView)
        inputPartDiameter = findViewById(R.id.inputPartDiameter)
        inputSawDiameter = findViewById(R.id.inputSawDiameter)
        inputRearSlotDepth = findViewById(R.id.inputRearSlotDepth)
        inputFrontSlotDepth = findViewById(R.id.inputFrontSlotDepth)
        btnCalculate = findViewById(R.id.btnCalculate)
        resultText = findViewById(R.id.resultText)

        btnCalculate.setOnClickListener { onCalculate() }
    }

    private fun onCalculate() {
        val partDiameter = parsePositiveDouble(inputPartDiameter, "Part Diameter")
        if (partDiameter == null) return

        val sawDiamStr = inputSawDiameter.text?.toString()?.trim() ?: ""
        val rearStr = inputRearSlotDepth.text?.toString()?.trim() ?: ""
        val frontStr = inputFrontSlotDepth.text?.toString()?.trim() ?: ""

        // If only part diameter is filled, just draw the part (Milestone 1)
        if (sawDiamStr.isEmpty() && rearStr.isEmpty() && frontStr.isEmpty()) {
            sawView.setPartOnly(partDiameter)
            resultText.setTextColor(0xFFDDDDDD.toInt())
            resultText.text = "Part Diameter: %.4f\"".format(partDiameter)
            return
        }

        // Full calculation (Milestone 2)
        val sawDiameter = parsePositiveDouble(inputSawDiameter, "Saw Diameter")
        if (sawDiameter == null) return

        val rearSlotDepth = parseDouble(inputRearSlotDepth, "Rear Slot Depth")
        if (rearSlotDepth == null) return

        val frontSlotDepth = parseDouble(inputFrontSlotDepth, "Front Slot Depth")
        if (frontSlotDepth == null) return

        // Validate that saw radius is large enough
        val sawRadius = sawDiameter / 2.0
        val partRadius = partDiameter / 2.0
        if (sawRadius <= partRadius) {
            showError("Saw radius (%.4f) must be larger than part radius (%.4f)".format(
                sawRadius, partRadius))
            return
        }

        sawView.setFullData(partDiameter, sawDiameter, rearSlotDepth, frontSlotDepth)

        val result = sawView.sawResult
        resultText.setTextColor(0xFFDDDDDD.toInt())
        if (result == null) {
            resultText.setTextColor(0xFFFF6666.toInt())
            resultText.text = "No intersections found.\nCheck that saw diameter is large enough."
        } else {
            val h = result.sawCenterX
            val k = result.sawCenterY
            val adjustment = SawGeometry.adjustmentText(h)
            resultText.text = buildString {
                append("h = %.4f\"   k = %.4f\"\n".format(h, k))
                append(adjustment)
            }
        }
    }

    /** Parse a positive double from an EditText, showing an error on failure. */
    private fun parsePositiveDouble(input: TextInputEditText, label: String): Double? {
        val text = input.text?.toString()?.trim() ?: ""
        if (text.isEmpty()) {
            showError("$label is required")
            input.requestFocus()
            return null
        }
        val value = text.toDoubleOrNull()
        if (value == null || value <= 0.0) {
            showError("$label must be a positive number")
            input.requestFocus()
            return null
        }
        return value
    }

    /** Parse a double (can be negative) from an EditText, showing an error on failure. */
    private fun parseDouble(input: TextInputEditText, label: String): Double? {
        val text = input.text?.toString()?.trim() ?: ""
        if (text.isEmpty()) {
            showError("$label is required")
            input.requestFocus()
            return null
        }
        val value = text.toDoubleOrNull()
        if (value == null) {
            showError("$label must be a valid number")
            input.requestFocus()
            return null
        }
        return value
    }

    private fun showError(msg: String) {
        resultText.text = msg
        resultText.setTextColor(0xFFFF6666.toInt())
    }
}
